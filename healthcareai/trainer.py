import time

import healthcareai.common.model_eval as hcaieval
import healthcareai.pipelines.data_preparation as pipelines
from healthcareai.advanced_trainer import AdvancedSupervisedModelTrainer


class SupervisedModelTrainer(object):
    def __init__(self, dataframe, predicted_column, model_type, impute=True, grain_column=None, verbose=False):
        self.grain_column = grain_column,
        self.predicted_column = predicted_column,
        self.grain_column = grain_column,
        self.grain_column = grain_column,

        # Build the pipeline
        pipeline = pipelines.full_pipeline(model_type, predicted_column, grain_column, impute=impute)

        # Run the raw data through the data preparation pipeline
        clean_dataframe = pipeline.fit_transform(dataframe)

        # Instantiate the advanced class
        self._advanced_trainer = AdvancedSupervisedModelTrainer(clean_dataframe, model_type, predicted_column,
                                                                grain_column, verbose)

        # Save the pipeline to the parent class
        self._advanced_trainer.pipeline = pipeline

        # Split the data into train and test
        self._advanced_trainer.train_test_split()

    def random_forest(self, save_plot=False):
        """ Train a random forest model and print out the model performance metrics. """
        # TODO Convenience method. Probably not needed?
        if self._advanced_trainer.model_type is 'classification':
            return self.random_forest_classification(save_plot=save_plot)
        elif self._advanced_trainer.model_type is 'regression':
            return self.random_forest_regression()

    def knn(self):
        """ Train a knn model and print out the model performance metrics. """
        model_name = 'KNN'
        print('Training {}'.format(model_name))
        t0 = time.time()

        # Train the model and display the model metrics
        trained_model = self._advanced_trainer.knn(scoring_metric='roc_auc', hyperparameter_grid=None,
                                                   randomized_search=True)
        print_training_results(model_name, t0, trained_model)

        return trained_model

    def random_forest_regression(self):
        """ Train a random forest regression model and print out the model performance metrics. """
        model_name = 'Random Forest Regression'
        print('Training {}'.format(model_name))
        t0 = time.time()

        # Train the model and display the model metrics
        trained_model = self._advanced_trainer.random_forest_regressor(trees=200,
                                                                       scoring_metric='neg_mean_squared_error',
                                                                       randomized_search=True)
        print_training_results(model_name, t0, trained_model)

        return trained_model

    def random_forest_classification(self, save_plot=False):
        """ Train a random forest classification model, print out performance metrics and show a ROC plot. """
        model_name = 'Random Forest Classification'
        print('Training {}'.format(model_name))
        t0 = time.time()

        # Train the model and display the model metrics
        trained_model = self._advanced_trainer.random_forest_classifier(trees=200, scoring_metric='roc_auc',
                                                                        randomized_search=True)
        print_training_results(model_name, t0, trained_model)

        # Save or show the feature importance graph
        hcaieval.plot_rf_from_tsm(trained_model, self._advanced_trainer.X_train, save=save_plot)

        return trained_model

    def logistic_regression(self):
        """ Train a logistic regression model and print out the model performance metrics. """
        model_name = 'Logistic Regression'
        print('Training {}'.format(model_name))
        t0 = time.time()

        # Train the model and display the model metrics
        trained_model = self._advanced_trainer.logistic_regression(randomized_search=False)
        print_training_results(model_name, t0, trained_model)

        return trained_model

    def linear_regression(self):
        """ Train a linear regression model and print out the model performance metrics. """
        model_name = 'Linear Regression'
        print('Training {}'.format(model_name))
        t0 = time.time()

        # Train the model and display the model metrics
        trained_model = self._advanced_trainer.linear_regression(randomized_search=False)
        print_training_results(model_name, t0, trained_model)

        return trained_model

    def ensemble(self):
        """ Train a ensemble model and print out the model performance metrics. """
        model_name = 'ensemble {}'.format(self._advanced_trainer.model_type)
        print('Training {}'.format(model_name))
        t0 = time.time()

        # Train the appropriate ensemble of models and display the model metrics
        if self._advanced_trainer.model_type is 'classification':
            metric = 'roc_auc'
            trained_model = self._advanced_trainer.ensemble_classification(scoring_metric=metric)
        elif self._advanced_trainer.model_type is 'regression':
            # TODO stub
            metric = 'neg_mean_squared_error'
            trained_model = self._advanced_trainer.ensemble_regression(scoring_metric=metric)

        print(
            'Based on the scoring metric {}, the best algorithm found is: {}'.format(metric,
                                                                                     trained_model.algorithm_name))

        print_training_results(model_name, t0, trained_model)

        return trained_model

    def get_advanced_features(self):
        return self._advanced_trainer


def print_training_timer(model_name, start_timestamp):
    """ Given an original timestamp, prints the amount of time that has passed. 

    Args:
        start_timestamp (float): Start time 
        model_name (str): model name
    """
    stop_time = time.time()
    delta_time = round(stop_time - start_timestamp, 2)
    print('Trained a {} model in {} seconds'.format(model_name, delta_time))


def print_training_results(model_name, t0, trained_model):
    """
    Print metrics, stats and hyperparameters of a training.
    Args:
        model_name (str): Name of the model 
        t0 (float): Training start time
        trained_model (TrainedSupervisedModel): The trained supervised model
    """
    print_training_timer(model_name, t0)

    hyperparameters = trained_model.best_hyperparameters
    if hyperparameters is None:
        hyperparameters = 'N/A: No hyperparameter search was performed'
    print("""Best hyperparameters found are:
        {}""".format(hyperparameters))

    if trained_model.is_classification:
        accuracy = trained_model.metrics['accuracy']
        roc_auc = trained_model.metrics['roc_auc']
        pr_auc = trained_model.metrics['pr_auc']

        print("""{} metrics:
            Accuracy: {}
            ROC AUC: {}
            PR AUC: {}""".format(model_name, accuracy, roc_auc, pr_auc))
    elif trained_model.is_regression:
        mean_squared_error = trained_model.metrics['mean_squared_error']
        mean_absolute_error = trained_model.metrics['mean_absolute_error']
        print("""{} metrics:
            Mean Squared Error (MSE): {}
            Mean Absolute Error (MAE): {}""".format(model_name, mean_squared_error, mean_absolute_error))