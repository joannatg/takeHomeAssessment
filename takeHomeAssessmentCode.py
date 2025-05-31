
import pandas as pd


# Load the CSV file
df = pd.read_csv("C:/Users/georgescuj/PycharmProjects/PythonProject/patient_id_month_year.csv")

# Convert 'month_year' to datetime
df['month_year'] = pd.to_datetime(df['month_year'])

# Sort by patient_id and month_year
df = df.sort_values(by=['patient_id', 'month_year'])

# Initialize result1 list
result1 = []

# Group by patient_id
for patient_id, group in df.groupby('patient_id'):
    group = group.reset_index(drop=True)
    start_date = group.loc[0, 'month_year']
    end_date = start_date

    for i in range(1, len(group)):
        current = group.loc[i, 'month_year']
        previous = group.loc[i - 1, 'month_year']

        # Check if current is the next month of previous
        if (current.year == previous.year and current.month == previous.month + 1) or \
           (current.year == previous.year + 1 and previous.month == 12 and current.month == 1):
            end_date = current + pd.offsets.MonthEnd(0)
        else:
            result1.append([patient_id, start_date, end_date])
            start_date = current
            end_date = current + pd.offsets.MonthEnd(0)

    result1.append([patient_id, start_date, end_date])

# Convert result to DataFrame
result1_df = pd.DataFrame(result1, columns=['patient_id', 'enrollment_start_date', 'enrollment_end_date'])

# Get number of rows
num_rows = result1_df.shape[0]
print("Number of rows:", num_rows)


# Save or display
print(result1_df)
result1_df.to_csv("patient_enrollment_span.csv", index=False)


#2

# Load the enrollment dataset
patient_enrollment_df = pd.read_csv("C:/Users/georgescuj/PycharmProjects/PythonProject/patient_enrollment_span.csv")

# Load the outpatient visits
outpatient_visits_df = pd.read_csv("C:/Users/georgescuj/PycharmProjects/PythonProject/outpatient_visits_file.csv")

# Convert date columns to datetime
patient_enrollment_df['enrollment_start_date'] = pd.to_datetime(patient_enrollment_df['enrollment_start_date'])
patient_enrollment_df['enrollment_end_date'] = pd.to_datetime(patient_enrollment_df['enrollment_end_date'])
outpatient_visits_df['date'] = pd.to_datetime(outpatient_visits_df['date'])

# Initialize the result2 DataFrame
result2_df = patient_enrollment_df.copy()

# Add columns for outpatient visit count and distinct days with outpatient visits
result2_df['outpatient_visit_count'] = 0
result2_df['ct_days_with_outpatient_visit'] = 0

# Calculate the outpatient visit count and distinct days with outpatient visits for each enrollment period
for i, row in result2_df.iterrows():
    patient_id = row['patient_id']
    start_date = row['enrollment_start_date']
    end_date = row['enrollment_end_date']

    # Filter outpatient visits for the patient within the enrollment period
    visits_within_period = outpatient_visits_df[
        (outpatient_visits_df['patient_id'] == patient_id) &
        (outpatient_visits_df['date'] >= start_date) &
        (outpatient_visits_df['date'] <= end_date)
        ]

    # Calculate the total outpatient visit count
    total_visits = visits_within_period['outpatient_visit_count'].sum()

    # Calculate the number of distinct days with outpatient visits
    distinct_days = visits_within_period['date'].nunique()

    # Update the result DataFrame
    result2_df.at[i, 'outpatient_visit_count'] = total_visits
    result2_df.at[i, 'ct_days_with_outpatient_visit'] = distinct_days

# Save the result to a CSV file
result2_df.to_csv('result.csv', index=False)


# Get the number of distinct values in 'ct_days_with_outpatient_visit' column
distinct_values_ct = result2_df['ct_days_with_outpatient_visit'].nunique()

print(f"The number of distinct values in 'ct_days_with_outpatient_visit' column is {distinct_values_ct}.")
# Save the result to a CSV file
result2_df.to_csv('result.csv', index=False)


#checks
#Does any patient_id have any visits outside of their enrollment period?
# Check for visits outside enrollment periods
def check_visits_outside_enrollment(patient_enrollment_df, outpatient_visits_df):
    for patient_id in patient_enrollment_df['patient_id'].unique():
        enrollment_periods = patient_enrollment_df[patient_enrollment_df['patient_id'] == patient_id]
        visits = outpatient_visits_df[outpatient_visits_df['patient_id'] == patient_id]

        for visit_date in visits['date']:
            within_enrollment = False
            for _, period in enrollment_periods.iterrows():
                if period['enrollment_start_date'] <= visit_date <= period['enrollment_end_date']:
                    within_enrollment = True
                    break
            if not within_enrollment:
                print(f"Patient {patient_id} has a visit on {visit_date.date()} outside of enrollment periods.")
                return False
    return True


# Check if any patient has visits outside enrollment periods
result = check_visits_outside_enrollment(patient_enrollment_df, outpatient_visits_df)

if result:
    print("No patient has visits outside their enrollment periods.")

 #Any patient_id with NO visits at all?
# Initialize a set to store patient IDs with visits
patients_with_visits = set(outpatient_visits_df['patient_id'].unique())

# Initialize a set to store patient IDs from enrollment dataset
patients_in_enrollment = set(patient_enrollment_df['patient_id'].unique())

# Find patients with no visits
patients_with_no_visits = patients_in_enrollment - patients_with_visits

# Print the result
if patients_with_no_visits:
    print(f"Patients with no visits at all: {', '.join(patients_with_no_visits)}")
else:
    print("All patients have at least one visit.")
