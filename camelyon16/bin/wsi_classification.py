import matplotlib.pyplot as plt
import pandas as pd
from sklearn import tree
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn import svm
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import roc_curve, auc
import sys
import os
import argparse
import logging
sys.path.append(os.path.dirname(os.path.abspath(__file__) + '/../../'))
#-----------------------------------------------------------------------------------------------------------------------
# 功能: 利用得到的特征训练特征分类器，并在测试集(测试集得到的特征集)进行测试
# 输入参考：
#         args.probs_map_features_train = 'G:/feature_csv/probs_map_features_train.csv'   训练集特征
#         args.probs_map_features_test = 'G:/feature_csv/probs_map_features_test.csv'     测试集的特征集
#         args.TEST_CSV_GT = 'G:/feature_csv/TEST_CSV_GT.csv'                             测试集的真实标签(用以评价模型的预测)
#-----------------------------------------------------------------------------------------------------------------------

FEATURE_START_INDEX = 6
parser = argparse.ArgumentParser(description='Train and test the wsi classification')
parser.add_argument('--probs_map_features_train', default=None, metavar='WSI_PATH', type=str,
                    help='Path to the input WSI file')
parser.add_argument('--probs_map_features_test', default=None, metavar='WSI_PATH', type=str,
                    help='Path to the input WSI file')
parser.add_argument('--TEST_CSV_GT', default=None, metavar='WSI_PATH', type=str,
                    help='Path to the input WSI file')

def plot_roc(gt_y, prob_predicted_y):
    predictions = prob_predicted_y[:, 1]
    gt_y = list(gt_y)
    fpr, tpr, _ = roc_curve(gt_y, predictions)

    roc_auc = auc(fpr, tpr)

    plt.figure(0).clf()
    # r'$\alpha_i > \beta_i$'
    plt.plot(fpr, tpr, 'b', label=r'$AUC_{Proposed} = %0.4f$' % roc_auc)

    plt.title('ROC curves')
    plt.plot([0, 1], [0, 1], 'k--')
    plt.xlim([0, 1])
    plt.ylim([0, 1])
    plt.ylabel('True Positive Rate')
    plt.xlabel('False Positive Rate')
    lg = plt.legend(loc='lower right', borderaxespad=1.)
    lg.get_frame().set_edgecolor('k')
    plt.grid(True, linestyle='-')
    plt.show()

def validate(x, gt_y, clf):
    predicted_y = clf.predict(x)
    prob_predicted_y = clf.predict_proba(x)
    logging.info('confusion matrix:')
    logging.info(pd.crosstab(gt_y, predicted_y, rownames=['Actual'], colnames=['Predicted']))

    return predicted_y, prob_predicted_y

def train(x, y):
    # clf = RandomForestClassifier(n_estimators=50, n_jobs=2)
    # clf.fit(x, y)

    # clf = KNeighborsClassifier(n_neighbors=5, weights='distance')
    # clf.fit(x, y)

    clf = svm.SVC(kernel='linear', C=1.5, probability=True)
    clf.fit(x, y)

    # clf = GaussianNB()
    # clf.fit(x, y)

    return clf

def load_train_test_data(f_train, f_test, args):
    df_train = pd.read_csv(f_train)
    df_test = pd.read_csv(f_test)
    df_test_gt = pd.read_csv(args.TEST_CSV_GT, header=None) # test 的标签
    # print(df_test_gt)
    df_test_gt.at[df_test_gt[1] == 'Tumor'] = 1
    df_test_gt.at[df_test_gt[1] == 'Normal'] = 0
    # print(df_test_gt)
    test_gt = df_test_gt.iloc[:, 1]
    n_columns = len(df_train.columns)
    feature_column_names = df_train.columns[FEATURE_START_INDEX:n_columns - 1]
    label_column_name = df_train.columns[n_columns - 1]
    return df_train[feature_column_names], df_train[label_column_name], df_test[feature_column_names], test_gt

def run(args):
    train_x, train_y, test_x, test_y = load_train_test_data(f_train=args.probs_map_features_train,
                                                            f_test=args.probs_map_features_test,args= args)
    model = train(train_x, train_y)
    predict_y, prob_predict_y = validate(test_x, test_y, model)
    plot_roc(test_y, prob_predict_y)

def main():
    logging.basicConfig(level=logging.INFO)
    args = parser.parse_args()
    args.probs_map_features_train ='G:/feature_csv/probs_map_features_train.csv'
    args.probs_map_features_test = 'G:/feature_csv/probs_map_features_test.csv'
    args.TEST_CSV_GT = 'G:/feature_csv/TEST_CSV_GT.csv'

    run(args)

if __name__ == '__main__':
    main()

