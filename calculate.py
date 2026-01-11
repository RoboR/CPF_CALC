from enum import Enum
from datetime import datetime
from datetime import timedelta
import calendar
import math


class CpfAccountType(Enum):
    ORDINARY = 1
    SPECIAL = 2
    MEDICAL = 3
    
class CpfAccount:
    #  ==========================     FIXED    ==========================
    # https://www.cpf.gov.sg/service/article/what-are-the-cpf-allocation-rates-for-2025
    CPF_CONTIBUTION_RATES_35_AND_BELOW = {CpfAccountType.ORDINARY : 0.6217, CpfAccountType.SPECIAL : 0.1621, CpfAccountType.MEDICAL : 0.2162}
    CPF_CONTIBUTION_RATES_36_TO_45 = {CpfAccountType.ORDINARY : 0.5677, CpfAccountType.SPECIAL : 0.1891, CpfAccountType.MEDICAL : 0.2432}
    CPF_CONTIBUTION_RATES_46_TO_50 = {CpfAccountType.ORDINARY : 0.5136, CpfAccountType.SPECIAL : 0.2162, CpfAccountType.MEDICAL : 0.2702}
    CPF_CONTIBUTION_RATES_51_TO_55 = {CpfAccountType.ORDINARY : 0.4055, CpfAccountType.SPECIAL : 0.3108 , CpfAccountType.MEDICAL : 0.2837}
    CPF_CONTIBUTION_RATES_56_TO_60 = {CpfAccountType.ORDINARY : 0.3694, CpfAccountType.SPECIAL : 0.3076, CpfAccountType.MEDICAL : 0.3230}
    CPF_CONTIBUTION_RATES_61_TO_65 = {CpfAccountType.ORDINARY : 0.149, CpfAccountType.SPECIAL : 0.4042, CpfAccountType.MEDICAL : 0.4468}
    CPF_CONTIBUTION_RATES_66_TO_70 = {CpfAccountType.ORDINARY: 0.0607 , CpfAccountType.SPECIAL : 0.303, CpfAccountType.MEDICAL : 0.6363}
    CPF_CONTIBUTION_RATES_ABOVE_70 = {CpfAccountType.ORDINARY : 0.08, CpfAccountType.SPECIAL : 0.08, CpfAccountType.MEDICAL : 0.84}
    
    # https://www.cpf.gov.sg/employer/infohub/news/cpf-related-announcements/new-contribution-rates
    # employer, employee rate
    CONTRIUBTION_RATE_55_AND_BELOW = (0.17, 0.2)
    CONTRIUBTION_RATE_55_TO_60 = (0.16, 0.18)
    CONTRIUBTION_RATE_60_TO_65 = (0.125, 0.125)
    CONTRIUBTION_RATE_65_TO_70 = (0.09, 0.75)
    CONTRIUBTION_RATE_ABOVE_70 = (0.075, 0.05)
    
    CONTRIUBTION_RATE_PR_FIRST_YEAR = (0.04, 0.05)
    CONTRIUBTION_RATE_PR_SECOND_YEAR = (0.09, 0.15)

    MA_MAX_AMOUNT = 75500  #https://www.cpf.gov.sg/service/article/is-there-a-maximum-amount-that-i-can-save-in-my-medisave-account
    FRS_MAX_AMOUNT = 228200    # https://www.cpf.gov.sg/service/article/how-much-is-my-full-retirement-sum
    CPF_MONTHLY_CEILING = 8000
    CPF_ANNUAL_LIMIT = 37740 # https://www.cpf.gov.sg/service/article/what-is-the-cpf-annual-limit

    def __init__(self, oaAmount, saAmount, maAmount, \
                 birthdate, prObtainedDate, retireDate, todayDate):
        self.accounts = dict()
        self.accounts[CpfAccountType.ORDINARY] = oaAmount
        self.accounts[CpfAccountType.SPECIAL] = saAmount
        self.accounts[CpfAccountType.MEDICAL] = maAmount
        self.birthdate = birthdate
        self.prObtainedDate = prObtainedDate
        self.todayDate = todayDate
        self.accountAllocation, self.contributionRate = self._generateContributionRatesDict()
        
        self.annualIncomeWithCpf = 0
        self.annualTaxableIncome = 0
        self.annualRelief = 0
        self.annualMonthlyWages = 0            # for pro-rated bonus and AWS
        self.previousYearWages = 0
        
        
    def ContributeIncomeWithCpf(self, grossIncome, onDate, isMonthlySalary, desc = ""):
        age = self._getNumberOfYears(self.birthdate, onDate)
        yearsOfPr = self._getNumberOfYears(self.prObtainedDate, onDate)

        allocationRate = self.accountAllocation[age]
        contributionRate = self.contributionRate[age]
        
        if (yearsOfPr < 2):
            contributionRate = CpfAccount.CONTRIUBTION_RATE_PR_FIRST_YEAR
        elif (yearsOfPr < 3):
            contributionRate = CpfAccount.CONTRIUBTION_RATE_PR_SECOND_YEAR
        
        employerRate, employeeRate = contributionRate
        
        cpfSalary = min(grossIncome, CpfAccount.CPF_MONTHLY_CEILING) if isMonthlySalary == True else grossIncome
        
        balanceCpfContribution = CpfAccount.CPF_ANNUAL_LIMIT - self.annualIncomeWithCpf
        #print("CPF balance contr ", balanceCpfContribution)

        employerContribution = (round(cpfSalary * employerRate * allocationRate[CpfAccountType.ORDINARY], 2),
                                round(cpfSalary * employerRate * allocationRate[CpfAccountType.SPECIAL], 2),
                                round(cpfSalary * employerRate * allocationRate[CpfAccountType.MEDICAL], 2))
                                
        employeeContribution = (round(cpfSalary * employeeRate * allocationRate[CpfAccountType.ORDINARY], 2),
                                round(cpfSalary * employeeRate * allocationRate[CpfAccountType.SPECIAL], 2),
                                round(cpfSalary * employeeRate * allocationRate[CpfAccountType.MEDICAL], 2))
                                
        totalContribution = tuple(round(sum(total), 2) for total in zip(employerContribution, employeeContribution))
        
        if (sum(totalContribution) > balanceCpfContribution):
            balanceRate = balanceCpfContribution / sum(totalContribution)
            employerContribution = tuple(amt * balanceRate for amt in employerContribution)
            employeeContribution = tuple(amt * balanceRate for amt in employeeContribution)
            totalContribution = tuple(amt * balanceRate for amt in totalContribution)
        
        # Annual computation
        self.annualMonthlyWages += grossIncome if isMonthlySalary else 0
        self.annualIncomeWithCpf += (sum(totalContribution))
        self.annualTaxableIncome += (grossIncome - sum(employeeContribution))
        
        #print("annual ", self.annualIncomeWithCpf, self.annualMonthlyWages, self.annualTaxableIncome)
        
        if (not isMonthlySalary):
            print("$$$ BONUS " + desc + " : " + str(round(grossIncome, 2)) + " $$$$")
        
        print("Employee contribution OA : " + str(round(employeeContribution[0], 2)) + ";  SA : " + str(round(employeeContribution[1], 2)) + " ; MA : " + str(round(employeeContribution[2], 2)))
        print("Employer contribution OA : " + str(round(employerContribution[0], 2)) + ";  SA : " + str(round(employerContribution[1], 2)) + " ; MA : " + str(round(employerContribution[2], 2)))
        print("Total contribution OA : " + str(round(totalContribution[0], 2)) + ";  SA : " + str(round(totalContribution[1], 2)) + " ; MA : " + str(round(totalContribution[2], 2)))
        
        self.accounts[CpfAccountType.ORDINARY] += totalContribution[0]
        self.accounts[CpfAccountType.SPECIAL] += totalContribution[1]
        self.accounts[CpfAccountType.MEDICAL] += totalContribution[2]
    
        self._adjustCpfAccounts()
    
    def TopUpAccount(self, topUps):
        oaTopUp, saTopUp, maTopUp = topUps
        
        if (not oaTopUp and not saTopUp and not maTopUp):
            return
            
        print("\n!!!  Topping up OA !!! : " + str(oaTopUp) + " ; SA : " + str(saTopUp) + " ; MA " + str(maTopUp))
        
        self.accounts[CpfAccountType.ORDINARY] += oaTopUp
        self.accounts[CpfAccountType.SPECIAL] += saTopUp
        self.accounts[CpfAccountType.MEDICAL] += maTopUp
        
        self._adjustCpfAccounts()
        
        self.annualRelief += sum(topUps)
        
    def ResetAnnualStatement(self, annualRelief):
        self.annualIncomeWithCpf = 0
        self.annualTaxableIncome = 0
        self.annualMonthlyWages = 0
        self.annualRelief = annualRelief
    
    def GetAge(self, today):
        return self._getNumberOfYears(self.birthdate, today)
        
    def _getAge(self):
        return self._getNumberOfYears(self.birthdate, self.todayDate)
        
    def _getNumberOfYears(self, fromDate, toDate):
        age = (toDate.year - fromDate.year - 1) 
        
        if (toDate.month > fromDate.month) or (toDate.month == fromDate.month and toDate.day >= fromDate.day):
            age += 1
            
        return age
        
    def ComputeMonthlyInterest(self):
        oaInterest, saInterest, maInterest = self._calculateMonthlyInterest()
        
        self.accounts[CpfAccountType.ORDINARY] += oaInterest
        self.accounts[CpfAccountType.SPECIAL] += saInterest
        self.accounts[CpfAccountType.MEDICAL] += maInterest
        
        print("Monthly Interest for OA : " + str(oaInterest) +  " ; SA : " + str(saInterest) + " ; MA : " + str(maInterest))

        self._adjustCpfAccounts()
        
    def GetTaxableIncome(self):
        
        totalTaxable = self.annualTaxableIncome
        totalTaxable -= 1000    # earned income relief
        totalTaxable -= self.annualRelief
        
        return round(totalTaxable, 2)
        
    # Adjust account with capping
    def _adjustCpfAccounts(self):
        # MA
        overflowAmount = max(0, (self.accounts[CpfAccountType.MEDICAL] - CpfAccount.MA_MAX_AMOUNT))
        self.accounts[CpfAccountType.MEDICAL] = min(self.accounts[CpfAccountType.MEDICAL], CpfAccount.MA_MAX_AMOUNT)
        
        # SA
        self.accounts[CpfAccountType.SPECIAL] += overflowAmount
        overflowAmount = max(0, self.accounts[CpfAccountType.SPECIAL] - CpfAccount.FRS_MAX_AMOUNT)
        self.accounts[CpfAccountType.SPECIAL] = min(self.accounts[CpfAccountType.SPECIAL], CpfAccount.FRS_MAX_AMOUNT)
        
        # OA
        self.accounts[CpfAccountType.ORDINARY] += overflowAmount
        
    def _calculateMonthlyInterest(self):
        # https://www.cpf.gov.sg/service/article/how-much-extra-interest-can-i-earn-on-my-cpf-savings
        OA_INTEREST_RATE = 0.025
        SA_INTEREST_RATE = 0.04
        MA_INTEREST_RATE = 0.04
        
        extraYearlyInterest = 0.01 if (self._getAge() < 55) else 0.02
        extraInterestCap = 60000
        oaExtraInterestCap = 20000
        oaInterest = 0
        saInterest = 0
        maInterest = 0
        
        # OA Interest
        oaAmountForExtraInterest = min(oaExtraInterestCap, self.accounts[CpfAccountType.ORDINARY])
        extraInterestCap = max(0, extraInterestCap - oaAmountForExtraInterest)
        oaInterest += (oaAmountForExtraInterest * extraYearlyInterest / 12)
        oaInterest += (self.accounts[CpfAccountType.ORDINARY] * OA_INTEREST_RATE / 12)
        
        # SA Interest
        saAmountForExtraInterest = min(extraInterestCap, self.accounts[CpfAccountType.SPECIAL])
        extraInterestCap = max(0, extraInterestCap - saAmountForExtraInterest)
        saInterest += (saAmountForExtraInterest * extraYearlyInterest / 12)
        saInterest += (self.accounts[CpfAccountType.SPECIAL] * SA_INTEREST_RATE / 12)
        
        # MA Interest
        maAmountForExtraInterest = min(extraInterestCap, self.accounts[CpfAccountType.MEDICAL])
        extraInterestCap = max(0, extraInterestCap - maAmountForExtraInterest)
        maInterest += (maAmountForExtraInterest * extraYearlyInterest / 12)
        maInterest += (self.accounts[CpfAccountType.MEDICAL] * MA_INTEREST_RATE / 12)
        
        return round(oaInterest, 2), round(saInterest, 2), round(maInterest, 2)
    
    def _computeTaxableIncome(self, grossIncome, cpfContributed):
        print("tax")
        
    def _generateContributionRatesDict(self, startWorkingAge = 18, endWorkingAge = 80):
        accountAllocationRate = dict()
        contributionRate = dict()
    
        for age in range(startWorkingAge, endWorkingAge):
            if (age <= 35):
                accountAllocationRate[age] = CpfAccount.CPF_CONTIBUTION_RATES_35_AND_BELOW
                contributionRate[age] = CpfAccount.CONTRIUBTION_RATE_55_AND_BELOW
            elif (age <= 45):
                accountAllocationRate[age] = CpfAccount.CPF_CONTIBUTION_RATES_36_TO_45
                contributionRate[age] = CpfAccount.CONTRIUBTION_RATE_55_AND_BELOW
            elif (age <= 50):
                accountAllocationRate[age] = CpfAccount.CPF_CONTIBUTION_RATES_46_TO_50
                contributionRate[age] = CpfAccount.CONTRIUBTION_RATE_55_AND_BELOW
            elif (age <= 55):
                accountAllocationRate[age] = CpfAccount.CPF_CONTIBUTION_RATES_51_TO_55
                contributionRate[age] = CpfAccount.CONTRIUBTION_RATE_55_AND_BELOW
            elif (age <= 60):
                accountAllocationRate[age] = CpfAccount.CPF_CONTIBUTION_RATES_56_TO_60
                contributionRate[age] = CpfAccount.CONTRIUBTION_RATE_55_TO_60
            elif (age <= 65):
                accountAllocationRate[age] = CpfAccount.CPF_CONTIBUTION_RATES_61_TO_65
                contributionRate[age] = CpfAccount.CONTRIUBTION_RATE_60_TO_65
            elif (age <= 70):
                accountAllocationRate[age] = CpfAccount.CPF_CONTIBUTION_RATES_66_TO_70
                contributionRate[age] = CpfAccount.CONTRIUBTION_RATE_65_TO_70
            else:
                accountAllocationRate[age] = CpfAccount.CPF_CONTIBUTION_RATES_ABOVE_70
                contributionRate[age] = CpfAccount.CONTRIUBTION_RATE_ABOVE_70
            
        return accountAllocationRate, contributionRate
        
        
    def log(self):
        msg = ""
        msg += "OA : " + str(round(self.accounts[CpfAccountType.ORDINARY], 2)) + ", "
        msg += "SA : " + str(round(self.accounts[CpfAccountType.SPECIAL], 2)) + ", "
        msg += "MA : " + str(round(self.accounts[CpfAccountType.MEDICAL], 2))
        
        return msg

# ------------------------------------------------------------------------------------------------------------


def GetNextMonthEndDate(readDateTime):
    # Get end date of this month
    readDateTime = readDateTime.replace(
    day=calendar.monthrange(readDateTime.year, readDateTime.month)[1])
    
    # First day of next month 
    readDateTime += timedelta(days=1)
    
    # Get end date of next month
    readDateTime = readDateTime.replace(
    day=calendar.monthrange(readDateTime.year, readDateTime.month)[1])
    
    return readDateTime

        
#  ==========================     USER SETTINGS    ==========================
USER_BIRTHDATE = datetime(1990, 10, 4)
#USER_PR_OBTAIN_DATE = datetime(2023, 1, 24)
USER_PR_OBTAIN_DATE = datetime(2017, 4, 10)
currentDate = datetime(2025, 8, 1)
# currentDate = datetime.now()
RETIRE_DATE =  datetime(2046, 10, 1)
CPF_OA_BALANCE = 70095.43
CPF_SA_BALANCE = 31182
CPF_MA_BALANCE = 32900.08

YEARLY_INCREMENT_RATE = 0.04  

CPF_VOLUNTARY_TOPUPS = \
{ # month : {OA, SA, MA}
    1 : (0, 0, 8000), 
    2 : (0, 0, 0), 
    3 : (0, 0, 0), 
    4 : (0, 0, 0), 
    5 : (0, 0, 0), 
    6 : (0, 0, 0), 
    7 : (0, 0, 0), 
    8 : (0, 0, 0), 
    9 : (0, 0, 0), 
    10 : (0, 0, 0),  
    11 : (0, 0, 0), 
    12 : (0, 0, 0)
}

ANNUAL_ADDITIONAL_RELIEF = 5000 # life insurance

YEARLY_BONUS = 1.8    # months
lastComputeDate = currentDate
baseSalary = 6500
FIRST_YEAR_AWS = True

myCpfAcc = CpfAccount(CPF_OA_BALANCE, CPF_SA_BALANCE, CPF_MA_BALANCE, USER_BIRTHDATE, USER_PR_OBTAIN_DATE, RETIRE_DATE, currentDate)


# Main loop calculation
while (((RETIRE_DATE - currentDate).days) >= 30):
    print(currentDate.date(), " Age : " + str(myCpfAcc.GetAge(currentDate)))
    
    if (currentDate.month == 1):
        myCpfAcc.ResetAnnualStatement(ANNUAL_ADDITIONAL_RELIEF)
    
    # compute last month interest
    if (lastComputeDate < currentDate):
        myCpfAcc.ComputeMonthlyInterest()
    
    # Check for voluntary contribution
    myCpfAcc.TopUpAccount(CPF_VOLUNTARY_TOPUPS[currentDate.month])
    
    # Annual increment
    if (currentDate.month == 4):
        baseSalary = round(baseSalary + baseSalary * YEARLY_INCREMENT_RATE, 2)
        print("%%%%%%%% Increment Salary to " + str(baseSalary) + " %%%%%%%%")
        
    # Contribute CPF from Salary
    myCpfAcc.ContributeIncomeWithCpf(baseSalary, currentDate, True)
    
    # Check bonus
    if (currentDate.month == 6):
        myCpfAcc.ContributeIncomeWithCpf(myCpfAcc.previousYearWages / 12 * YEARLY_BONUS, currentDate, False, "Yearly")
    if (currentDate.month == 12):
        if (FIRST_YEAR_AWS == True):
            myCpfAcc.previousYearWages = myCpfAcc.annualMonthlyWages
            FIRST_YEAR_AWS = False
            
        myCpfAcc.ContributeIncomeWithCpf(myCpfAcc.previousYearWages / 12, currentDate, False, "AWS")
        myCpfAcc.previousYearWages = myCpfAcc.annualMonthlyWages
        
    # log
    print(myCpfAcc.log() + "\n")
    
    if (currentDate.month == 12):
        print("Taxable income : " + str(myCpfAcc.GetTaxableIncome()))
        print("===============================================================")
    
    # step to next month
    lastComputeDate = currentDate
    currentDate = GetNextMonthEndDate(currentDate)
    

