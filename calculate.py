from datetime import datetime
from datetime import timedelta
import calendar
import math


#FIXED
# https://www.cpf.gov.sg/service/article/what-are-the-cpf-allocation-rates-for-2025
CPF_CONTIBUTION_RATES_35_AND_BELOW = {"OA" : 0.6217, "SA" : 0.1621, "MA" : 0.2162}
CPF_CONTIBUTION_RATES_36_TO_45 = {"OA" : 0.5677, "SA" : 0.1891, "MA" : 0.2432}
CPF_CONTIBUTION_RATES_46_TO_50 = {"OA" : 0.5136, "SA" : 0.2162, "MA" : 0.2702}
CPF_CONTIBUTION_RATES_51_TO_55 = {"OA" : 0.4055, "SA" : 0.3108 , "MA" : 0.2837}
CPF_CONTIBUTION_RATES_56_TO_60 = {"OA" : 0.3694, "SA" : 0.3076, "MA" : 0.3230}
CPF_CONTIBUTION_RATES_61_TO_65 = {"OA" : 0.149, "SA" : 0.4042, "MA" : 0.4468}
CPF_CONTIBUTION_RATES_66_TO_70 = {"OA" : 0.0607 , "SA" : 0.303, "MA" : 0.6363}
CPF_CONTIBUTION_RATES_ABOVE_70 = {"OA" : 0.08, "SA" : 0.08, "MA" : 0.84}

# https://www.cpf.gov.sg/employer/infohub/news/cpf-related-announcements/new-contribution-rates
# employer, employee rate
CONTRIUBTION_RATE_55_AND_BELOW = (0.17, 0.2)
CONTRIUBTION_RATE_55_TO_60 = (0.16, 0.18)
CONTRIUBTION_RATE_60_TO_65 = (0.125, 0.125)
CONTRIUBTION_RATE_65_TO_70 = (0.09, 0.75)
CONTRIUBTION_RATE_ABOVE_70 = (0.075, 0.05)

CONTRIUBTION_RATE_PR_FIRST_YEAR = (0.04, 0.05)
CONTRIUBTION_RATE_PR_SECOND_YEAR = (0.09, 0.15)

def GenerateContributionRatesDict(startWorkingAge, endWorkingAge):
    accountAllocationRate = dict()
    contributionRate = dict()

    for age in range(startWorkingAge, endWorkingAge):
        if (age <= 35):
            accountAllocationRate[age] = CPF_CONTIBUTION_RATES_35_AND_BELOW
            contributionRate[age] = CONTRIUBTION_RATE_55_AND_BELOW
        elif (age <= 45):
            accountAllocationRate[age] = CPF_CONTIBUTION_RATES_36_TO_45
            contributionRate[age] = CONTRIUBTION_RATE_55_AND_BELOW
        elif (age <= 50):
            accountAllocationRate[age] = CPF_CONTIBUTION_RATES_46_TO_50
            contributionRate[age] = CONTRIUBTION_RATE_55_AND_BELOW
        elif (age <= 55):
            accountAllocationRate[age] = CPF_CONTIBUTION_RATES_51_TO_55
            contributionRate[age] = CONTRIUBTION_RATE_55_AND_BELOW
        elif (age <= 60):
            accountAllocationRate[age] = CPF_CONTIBUTION_RATES_56_TO_60
            contributionRate[age] = CONTRIUBTION_RATE_55_TO_60
        elif (age <= 65):
            accountAllocationRate[age] = CPF_CONTIBUTION_RATES_61_TO_65
            contributionRate[age] = CONTRIUBTION_RATE_60_TO_65
        elif (age <= 70):
            accountAllocationRate[age] = CPF_CONTIBUTION_RATES_66_TO_70
            contributionRate[age] = CONTRIUBTION_RATE_65_TO_70
        else:
            accountAllocationRate[age] = CPF_CONTIBUTION_RATES_ABOVE_70
            contributionRate[age] = CONTRIUBTION_RATE_ABOVE_70
        
    return accountAllocationRate, contributionRate
    
CPF_ACCOUNT_ALLOCATION_RATE, CPF_CONTRIBUTION_RATE = GenerateContributionRatesDict(13, 100)


CPF_MA_MAX_AMOUNT = 75500  #https://www.cpf.gov.sg/service/article/is-there-a-maximum-amount-that-i-can-save-in-my-medisave-account
FRS_MAX_AMOUNT = 228200    # https://www.cpf.gov.sg/service/article/how-much-is-my-full-retirement-sum
CPF_MONTHLY_CEILING = 8000
CPF_ANNUAL_LIMIT = 37740 # https://www.cpf.gov.sg/service/article/what-is-the-cpf-annual-limit

# https://www.cpf.gov.sg/service/article/how-much-extra-interest-can-i-earn-on-my-cpf-savings
def CalculateMonthlyCPFInterest(age, OABalance, SABalance, MABalance):
    # yearly interest
    OA_INTEREST_RATE = 0.025
    SA_INTEREST_RATE = 0.04
    MA_INTEREST_RATE = 0.04
    
    extraYearlyInterest = 0.01 if (age < 55) else 0.02
    extraInterestCap = 60000
    oaExtraInterestCap = 20000
    oaInterest = 0
    saInterest = 0
    maInterest = 0
    
    # OA Interest
    oaAmountForExtraInterest = min(oaExtraInterestCap, OABalance)
    extraInterestCap = max(0, extraInterestCap - oaAmountForExtraInterest)
    oaInterest += (oaAmountForExtraInterest * extraYearlyInterest / 12)
    oaInterest += (OABalance * OA_INTEREST_RATE / 12)
    
    # SA Interest
    saAmountForExtraInterest = min(extraInterestCap, SABalance)
    extraInterestCap = max(0, extraInterestCap - saAmountForExtraInterest)
    saInterest += (saAmountForExtraInterest * extraYearlyInterest / 12)
    saInterest += (SABalance * SA_INTEREST_RATE / 12)
    
    # MA Interest
    maAmountForExtraInterest = min(extraInterestCap, MABalance)
    extraInterestCap = max(0, extraInterestCap - maAmountForExtraInterest)
    maInterest += (maAmountForExtraInterest * extraYearlyInterest / 12)
    maInterest += (MABalance * MA_INTEREST_RATE / 12)
    
    return round(oaInterest, 2), round(saInterest, 2), round(maInterest, 2)

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
    
def GetMonthCpfContributions(salary, age, prContributionRate=None):
    allocationRate = CPF_ACCOUNT_ALLOCATION_RATE[age]
    employerRate, employeeRate = prContributionRate if (prContributionRate) else CPF_CONTRIBUTION_RATE[age]
    
    cpfSalary = min(salary, CPF_MONTHLY_CEILING)
    
    employerContribution = (round(cpfSalary * employerRate * allocationRate['OA'], 2),
                            round(cpfSalary * employerRate * allocationRate['SA'], 2),
                            round(cpfSalary * employerRate * allocationRate['MA'], 2))
    
    employeeContribution = (round(cpfSalary * employeeRate * allocationRate['OA'], 2),
                            round(cpfSalary * employeeRate * allocationRate['SA'], 2),
                            round(cpfSalary * employeeRate * allocationRate['MA'], 2))
    
    return employerContribution, employeeContribution
    
def GetBonusContributions(bonus, age, yearlyCpfContribution):
    allocationRate = CPF_ACCOUNT_ALLOCATION_RATE[age]
    employerRate, employeeRate = CPF_CONTRIBUTION_RATE[age]
    
    balanceContribution = max(0, (CPF_ANNUAL_LIMIT - yearlyCpfContribution))
    cpfForBonus = min(balanceContribution / (employerRate + employeeRate), bonus)
    
    employerContribution = (round(cpfForBonus * employerRate * allocationRate['OA'], 2),
                            round(cpfForBonus * employerRate * allocationRate['SA'], 2),
                            round(cpfForBonus * employerRate * allocationRate['MA'], 2))
    
    employeeContribution = (round(cpfForBonus * employeeRate * allocationRate['OA'], 2),
                            round(cpfForBonus * employeeRate * allocationRate['SA'], 2),
                            round(cpfForBonus * employeeRate * allocationRate['MA'], 2))
    
    return employerContribution, employeeContribution

def AdjustCpfAccounts(oaAmount, saAmount, maAmount):
    overFlowAmount = max(0, (maAmount - CPF_MA_MAX_AMOUNT))
    if (not overFlowAmount):
        return oaAmount, saAmount, maAmount
        
    maAmount = min(maAmount, CPF_MA_MAX_AMOUNT)
    
    saAmount += overFlowAmount
    overFlowAmount = max(0, saAmount - FRS_MAX_AMOUNT)
    saAmount = min(saAmount, FRS_MAX_AMOUNT)
    
    oaAmount += overFlowAmount
    
    return oaAmount, saAmount, maAmount

# USER SETTINGS
USER_BIRTHDATE = datetime(1990, 10, 4)
USER_PR_OBTAIN_DATE = datetime(2017, 4, 10)
currentDate = datetime(2025, 8, 1)#datetime.now()
RETIRE_DATE =  datetime(2055, 10, 5)

MONTHLY_INCOME = 6500
CPF_OA_BALANCE = 72104.46
CPF_SA_BALANCE = 31707.52
CPF_MA_BALANCE = 33600.99

endOfTheMonth = currentDate
salary = MONTHLY_INCOME
oaAmount = CPF_OA_BALANCE
saAmount = CPF_SA_BALANCE
maAmount = CPF_MA_BALANCE
yearlyTaxableIncome = 0
yearlyCpfContribution = 0

HAS_AWS = True
YEARLY_BONUS = 2
grossSalary = 0
preYearGrosSalary = 0
awsAmount = 0
yearlyIncrementRate = 0.03


# Main loop calculation
while (((RETIRE_DATE - endOfTheMonth).days) >= 30):
    userAge = int((endOfTheMonth - USER_BIRTHDATE).days / 365)
    
    if endOfTheMonth.month == 1:
        print("\nLast year taxable income =", round(yearlyTaxableIncome, 2),
              "; CPF total contribuition =", round(yearlyCpfContribution, 2))
        yearlyTaxableIncome = 0
        preYearGrosSalary = grossSalary
        grossSalary = 0
        awsAmount = 0
        yearlyCpfContribution = 0

    grossSalary += salary
    
    # Monthly incremental
    oaInterest, saInterest, maInterest = CalculateMonthlyCPFInterest(userAge, oaAmount, saAmount, maAmount)
    
    prContributionRate = None
    
    # Simplify version as below 55 years
    if USER_PR_OBTAIN_DATE:
        prYear = math.ceil(((endOfTheMonth.year - USER_PR_OBTAIN_DATE.year) * 12 + 
                       (endOfTheMonth.month - USER_PR_OBTAIN_DATE.month))/ 12)
       
        if (prYear <= 1):
           prContributionRate = CONTRIUBTION_RATE_PR_FIRST_YEAR
        elif (prYear <= 2):
           prContributionRate = CONTRIUBTION_RATE_PR_SECOND_YEAR
           
    employerContribution, employeeContribution = GetMonthCpfContributions(salary, userAge, prContributionRate)
    
    oaAmount = round(oaAmount + oaInterest + employerContribution[0] + employeeContribution[0], 2)
    saAmount = round(saAmount + saInterest + employerContribution[1] + employeeContribution[1], 2)
    maAmount = round(maAmount + maInterest + employerContribution[2] + employeeContribution[2], 2)
    
    yearlyTaxableIncome += (salary - employeeContribution[0] - employeeContribution[1] - employeeContribution[2])
    yearlyCpfContribution += (employerContribution[0] + employerContribution[1] + employerContribution[2] +
                              employeeContribution[0] + employeeContribution[1] + employeeContribution[2])
    
    oaAmount, saAmount, maAmount = AdjustCpfAccounts(oaAmount, saAmount, maAmount)
    
    # AWS Bonus
    if HAS_AWS and endOfTheMonth.month == 12:
        awsAmount = round(grossSalary / 12, 2)
        awsEmployerContribution, awsEmployeeContribution = GetBonusContributions(awsAmount, userAge, yearlyCpfContribution)
        oaAmount =  round(oaAmount + awsEmployerContribution[0] + awsEmployeeContribution[0], 2)
        saAmount =  round(saAmount + awsEmployerContribution[1] + awsEmployeeContribution[1], 2)
        maAmount =  round(maAmount + awsEmployerContribution[1] + awsEmployeeContribution[2], 2)
        print("AWS : ", awsAmount, ";CPF", awsEmployerContribution, awsEmployeeContribution)

        yearlyTaxableIncome += (awsAmount - awsEmployeeContribution[0] - awsEmployeeContribution[1] - awsEmployeeContribution[2])
        yearlyCpfContribution += (awsEmployerContribution[0] + awsEmployerContribution[1] + awsEmployerContribution[2] +
                                  awsEmployeeContribution[0] + awsEmployeeContribution[1] + awsEmployeeContribution[2])
        oaAmount, saAmount, maAmount = AdjustCpfAccounts(oaAmount, saAmount, maAmount)
        
    # Yearly Bonus
    elif YEARLY_BONUS and endOfTheMonth.month == 3:
        yearlyBonus = (preYearGrosSalary / 12) * YEARLY_BONUS
        
        bonusEmployerContribution, bonusEmployeeContribution = GetBonusContributions(yearlyBonus, userAge, yearlyCpfContribution)
        print("!!!!!BONUS!!!!! : ", yearlyBonus, ";CPF", bonusEmployerContribution, bonusEmployeeContribution)

        oaAmount =  round(oaAmount + bonusEmployerContribution[0] + bonusEmployeeContribution[0], 2)
        saAmount =  round(saAmount + bonusEmployerContribution[1] + bonusEmployeeContribution[1], 2)
        maAmount =  round(maAmount + bonusEmployerContribution[1] + bonusEmployeeContribution[2], 2)
        
        yearlyTaxableIncome += (yearlyBonus - bonusEmployeeContribution[0] - bonusEmployeeContribution[1] - bonusEmployeeContribution[2])
        yearlyCpfContribution += (bonusEmployerContribution[0] + bonusEmployerContribution[1] + bonusEmployerContribution[2] +
                                  bonusEmployeeContribution[0] + bonusEmployeeContribution[1] + bonusEmployeeContribution[2])
        oaAmount, saAmount, maAmount = AdjustCpfAccounts(oaAmount, saAmount, maAmount)
    
    # Increment
    elif yearlyIncrementRate and endOfTheMonth.month == 7:
        salary += (salary * yearlyIncrementRate)
        
    # Add CPF volunter contribution and tax deduction
        
    print(endOfTheMonth.strftime("%Y-%m-%d"), 
    "; Age", userAge, 
    "; Salary ", salary,
    "; EMPLOYER CPF :", employerContribution, 
    "; EMPLOYEE CPF :", employeeContribution, 
    "; CPF Interest :", oaInterest, saInterest, maInterest,
    "; CPF Accounts :", oaAmount, saAmount, maAmount,
    "; taxable income:", round(yearlyTaxableIncome, 2))
    
    endOfTheMonth = GetNextMonthEndDate(endOfTheMonth)
    


