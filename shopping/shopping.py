import csv
import sys

from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

TEST_SIZE = 0.4


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python shopping.py data")

    # Load data from spreadsheet and split into train and test sets
    evidence, labels = load_data(sys.argv[1])

    X_train, X_test, y_train, y_test = train_test_split(
        evidence, labels, test_size=TEST_SIZE
    )
    # Train model and make predictions
    model = train_model(X_train, y_train)
    predictions = model.predict(X_test)
    sensitivity, specificity = evaluate(y_test, predictions)

    # Print results
    print(f"Correct: {(y_test == predictions).sum()}")
    print(f"Incorrect: {(y_test != predictions).sum()}")
    print(f"True Positive Rate: {100 * sensitivity:.2f}%")
    print(f"True Negative Rate: {100 * specificity:.2f}%")


def load_data(filename):
    """
    Load shopping data from a CSV file `filename` and convert into a list of
    evidence lists and a list of labels. Return a tuple (evidence, labels).

    evidence should be a list of lists, where each list contains the
    following values, in order:
        - Administrative, an integer
        - Administrative_Duration, a floating point number
        - Informational, an integer
        - Informational_Duration, a floating point number
        - ProductRelated, an integer
        - ProductRelated_Duration, a floating point number
        - BounceRates, a floating point number
        - ExitRates, a floating point number
        - PageValues, a floating point number
        - SpecialDay, a floating point number
        - Month, an index from 0 (January) to 11 (December)
        - OperatingSystems, an integer
        - Browser, an integer
        - Region, an integer
        - TrafficType, an integer
        - VisitorType, an integer 0 (not returning) or 1 (returning)
        - Weekend, an integer 0 (if false) or 1 (if true)

    labels should be the corresponding list of labels, where each label
    is 1 if Revenue is true, and 0 otherwise.
    """
    evidence = list()
    labels = list()
    # init type for each value
    # for int value
    evi_int = ['Administrative', 'Informational', 'ProductRelated',
               'OperatingSystems', 'Browser', 'Region', 'TrafficType']
    # for float value
    evi_float = ['Administrative_Duration', 'Informational_Duration',
                 'ProductRelated_Duration', 'BounceRates', 'ExitRates', 'PageValues', 'SpecialDay']
    # for month value  
    evi_month = {'Jan': 0, 'Feb': 1, 'Mar': 2, 'Apr': 3, 'May': 4, 'June': 5,
                 'Jul': 6, 'Aug': 7, 'Sep': 8, 'Oct': 9, 'Nov': 10, 'Dec': 11}
    # for visitor type value
    evi_vistor_type = {'Returning_Visitor': 1, 'New_Visitor': 0, 'Other':0}
    # for weekend value
    evi_weekend = {'TRUE': 1, 'FALSE': 0}

    with open("shopping.csv") as f:
        reader = csv.reader(f)
        # read first line as header
        header = next(reader)
        # read evidence, labels
        for row in reader:
            evidence.append([determine_type(header[id], value, evi_int, evi_float, evi_month, evi_vistor_type,
                                    evi_weekend) for (id, value) in enumerate(row[:-1])])
            labels.append(1 if row[-1] == 'TRUE' else 0)
        return (evidence, labels)
    
    return (None, None)

def train_model(evidence, labels):
    """
    Given a list of evidence lists and a list of labels, return a
    fitted k-nearest neighbor model (k=1) trained on the data.
    """
    model = KNeighborsClassifier(n_neighbors=1)
    model.fit(evidence, labels)
    return model

def evaluate(labels, predictions):
    """
    Given a list of actual labels and a list of predicted labels,
    return a tuple (sensitivity, specificty).

    Assume each label is either a 1 (positive) or 0 (negative).

    `sensitivity` should be a floating-point value from 0 to 1
    representing the "true positive rate": the proportion of
    actual positive labels that were accurately identified.

    `specificity` should be a floating-point value from 0 to 1
    representing the "true negative rate": the proportion of
    actual negative labels that were accurately identified.
    """
    sensitivity = [label == predict_label for (label, predict_label) in zip(labels, predictions) if label == 1]
    specificity = [label == predict_label for (label, predict_label) in zip(labels, predictions) if label == 0]
    return (sum(sensitivity)/len(sensitivity), sum(specificity)/len(specificity))

def determine_type(evidence, value, evi_int, evi_float, evi_month, evi_visitor_type, evi_weekend):
    if evidence in evi_int:
        return int(value)
    if evidence in evi_float:
        return float(value)
    if value in evi_month:
        return evi_month[value]
    if value in evi_visitor_type:
        return evi_visitor_type[value]
    if value in evi_weekend:
        return evi_weekend[value]
    return None


if __name__ == "__main__":
    main()
