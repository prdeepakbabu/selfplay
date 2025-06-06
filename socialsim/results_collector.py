"""
Results collection and analysis for SocialSim.

This module defines the ResultsCollector class, which collects and analyzes
the results of social science experiments.
"""

import json
import time
import logging
from typing import List, Dict, Any, Optional, Union
import pandas as pd
import numpy as np
from scipy import stats

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ResultsCollector:
    """
    A class for collecting and analyzing the results of social science experiments.
    
    This class aggregates responses from all personas, provides methods for exporting
    to various formats, and includes metadata about the experiment setup.
    """
    
    def __init__(self, experiment_config):
        """
        Initialize the ResultsCollector.
        
        Args:
            experiment_config (dict): Configuration of the experiment
        """
        self.experiment_config = experiment_config
        self.responses = []
        self.start_time = time.time()
        self.end_time = None
    
    def add_response(self, response):
        """
        Add a response to the collector.
        
        Args:
            response (SurveyResponse): Response to add
        """
        self.responses.append(response)
    
    def finalize(self):
        """
        Finalize the results collection.
        """
        self.end_time = time.time()
        logger.info(f"Collected {len(self.responses)} responses in {self.end_time - self.start_time:.2f} seconds")
    
    def get_dataframe(self):
        """
        Convert responses to pandas DataFrame for analysis.
        
        Returns:
            pd.DataFrame: DataFrame containing all responses
        """
        # Extract response data
        data = []
        for response in self.responses:
            row = {
                'survey_id': response.survey_id,
                'question_id': response.question_id,
                'question_text': response.question_text,
                'question_type': response.question_type,
                'question_variant': response.question_variant,
                'persona_id': response.persona_id,
                'response_value': response.response_value,
                'response_time': response.response_time,
                'confidence_score': response.confidence_score,
                'group': response.group,
                'condition': response.condition
            }
            
            # Add persona attributes as columns
            for key, value in response.persona_attributes.items():
                # Skip complex nested structures
                if not isinstance(value, (dict, list)):
                    row[f'persona_{key}'] = value
            
            data.append(row)
        
        return pd.DataFrame(data)
    
    def export_csv(self, filepath):
        """
        Export results to CSV.
        
        Args:
            filepath (str): Path to save the CSV file
        """
        df = self.get_dataframe()
        df.to_csv(filepath, index=False)
        logger.info(f"Exported {len(self.responses)} responses to {filepath}")
    
    def export_json(self, filepath):
        """
        Export results to JSON.
        
        Args:
            filepath (str): Path to save the JSON file
        """
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
        logger.info(f"Exported {len(self.responses)} responses to {filepath}")
    
    def to_dict(self):
        """
        Convert all data to dictionary format.
        
        Returns:
            dict: Dictionary containing all data
        """
        return {
            "experiment_config": self.experiment_config,
            "metadata": {
                "start_time": self.start_time,
                "end_time": self.end_time,
                "total_responses": len(self.responses),
                "duration": self.end_time - self.start_time if self.end_time else None
            },
            "responses": [r.__dict__ for r in self.responses]
        }
    
    def summary_statistics(self):
        """
        Generate basic summary statistics.
        
        Returns:
            dict: Dictionary containing summary statistics
        """
        df = self.get_dataframe()
        
        # For multiple choice questions, calculate frequency distribution
        if self.experiment_config.get('question_type') == 'multiple_choice':
            response_counts = df['response_value'].value_counts()
            response_percentages = response_counts / len(df) * 100
            
            summary = {
                'total_responses': len(df),
                'response_counts': response_counts.to_dict(),
                'response_percentages': response_percentages.to_dict()
            }
            
            # If we have demographic data, break down by demographics
            demographic_columns = [col for col in df.columns if col.startswith('persona_')]
            if demographic_columns:
                demographic_breakdowns = {}
                
                for col in demographic_columns:
                    if df[col].nunique() <= 10:  # Only break down for categorical variables with few categories
                        breakdown = df.groupby(col)['response_value'].value_counts().unstack().fillna(0)
                        demographic_breakdowns[col] = breakdown.to_dict()
                
                summary['demographic_breakdowns'] = demographic_breakdowns
            
            return summary
        
        # For numeric responses, calculate descriptive statistics
        elif self.experiment_config.get('question_type') == 'numeric':
            try:
                df['response_value'] = pd.to_numeric(df['response_value'])
                
                summary = {
                    'total_responses': len(df),
                    'mean': df['response_value'].mean(),
                    'median': df['response_value'].median(),
                    'std_dev': df['response_value'].std(),
                    'min': df['response_value'].min(),
                    'max': df['response_value'].max(),
                    'quartiles': {
                        '25%': df['response_value'].quantile(0.25),
                        '50%': df['response_value'].quantile(0.5),
                        '75%': df['response_value'].quantile(0.75)
                    }
                }
                
                return summary
            except:
                logger.warning("Could not convert response values to numeric for statistical analysis")
                return {'total_responses': len(df)}
        
        # Default case
        return {'total_responses': len(df)}
    
    def compare_groups(self, group_column='group', paired=False, persona_column='persona_id'):
        """
        Compare results between different groups (e.g., for A/B testing).
        
        Args:
            group_column (str): Column to group by
            paired (bool): Whether to treat the data as paired (within-subjects design)
            persona_column (str): Column containing persona identifiers (for paired analysis)
            
        Returns:
            dict: Dictionary containing comparison results
        """
        df = self.get_dataframe()
        
        if group_column not in df.columns or df[group_column].nunique() <= 1:
            logger.warning(f"Cannot compare groups: column '{group_column}' not found or has only one value")
            return None
        
        # For multiple choice questions
        if self.experiment_config.get('question_type') == 'multiple_choice':
            # Calculate response distributions for each group
            group_distributions = {}
            
            for group, group_df in df.groupby(group_column):
                response_counts = group_df['response_value'].value_counts()
                response_percentages = response_counts / len(group_df) * 100
                
                group_distributions[group] = {
                    'total_responses': len(group_df),
                    'response_counts': response_counts.to_dict(),
                    'response_percentages': response_percentages.to_dict()
                }
            
            # Determine if this is a within-subjects design
            is_within_subjects = paired and persona_column in df.columns
            
            # For within-subjects design, perform McNemar's test
            if is_within_subjects and df[group_column].nunique() == 2:
                significance_result = self._perform_mcnemars_test(df, group_column, persona_column)
            # For between-subjects design, perform chi-square test
            else:
                try:
                    from scipy.stats import chi2_contingency
                    
                    # Create contingency table
                    contingency_table = pd.crosstab(df[group_column], df['response_value'])
                    
                    # Perform chi-square test
                    chi2, p_value, dof, expected = chi2_contingency(contingency_table)
                    
                    significance_result = {
                        'test': 'chi2_contingency',
                        'chi2': chi2,
                        'p_value': p_value,
                        'degrees_of_freedom': dof,
                        'significant_at_0.05': p_value < 0.05
                    }
                except Exception as e:
                    logger.warning(f"Could not perform chi-square test: {str(e)}")
                    significance_result = None
            
            return {
                'group_distributions': group_distributions,
                'significance_test': significance_result
            }
        
        # For numeric responses
        elif self.experiment_config.get('question_type') == 'numeric':
            try:
                df['response_value'] = pd.to_numeric(df['response_value'])
                
                # Calculate descriptive statistics for each group
                group_statistics = {}
                
                for group, group_df in df.groupby(group_column):
                    group_statistics[group] = {
                        'total_responses': len(group_df),
                        'mean': group_df['response_value'].mean(),
                        'median': group_df['response_value'].median(),
                        'std_dev': group_df['response_value'].std()
                    }
                
                # Perform t-test if there are exactly 2 groups
                if df[group_column].nunique() == 2:
                    try:
                        from scipy.stats import ttest_ind
                        
                        groups = df[group_column].unique()
                        group1_values = df[df[group_column] == groups[0]]['response_value']
                        group2_values = df[df[group_column] == groups[1]]['response_value']
                        
                        t_stat, p_value = ttest_ind(group1_values, group2_values)
                        
                        significance_result = {
                            'test': 'ttest_ind',
                            't_statistic': t_stat,
                            'p_value': p_value,
                            'significant_at_0.05': p_value < 0.05
                        }
                    except:
                        logger.warning("Could not perform t-test")
                        significance_result = None
                # Perform ANOVA if there are more than 2 groups
                else:
                    try:
                        from scipy.stats import f_oneway
                        
                        groups = df[group_column].unique()
                        group_values = [df[df[group_column] == group]['response_value'] for group in groups]
                        
                        f_stat, p_value = f_oneway(*group_values)
                        
                        significance_result = {
                            'test': 'f_oneway',
                            'f_statistic': f_stat,
                            'p_value': p_value,
                            'significant_at_0.05': p_value < 0.05
                        }
                    except:
                        logger.warning("Could not perform ANOVA")
                        significance_result = None
                
                return {
                    'group_statistics': group_statistics,
                    'significance_test': significance_result
                }
            except:
                logger.warning("Could not convert response values to numeric for statistical analysis")
                return None
        
        # Default case
        return None
    
    def _perform_mcnemars_test(self, df, group_column, persona_column):
        """
        Perform McNemar's test for paired nominal data.
        
        Args:
            df (pd.DataFrame): DataFrame containing the data
            group_column (str): Column containing group labels
            persona_column (str): Column containing persona identifiers
            
        Returns:
            dict: Dictionary containing test results
        """
        try:
            # Get the two group labels
            groups = df[group_column].unique()
            if len(groups) != 2:
                logger.warning(f"McNemar's test requires exactly 2 groups, but found {len(groups)}")
                return None
            
            # Create a pivot table to get paired responses
            pivot = df.pivot_table(
                index=persona_column,
                columns=group_column,
                values='response_value',
                aggfunc='first'
            )
            
            # For binary responses (e.g., Yes/No), create a contingency table
            # We'll focus on the most common response (usually "Yes") vs. all others
            most_common_response = df['response_value'].value_counts().index[0]
            
            # Count the different response patterns
            a = 0  # Yes to both
            b = 0  # Yes to group1, No to group2
            c = 0  # No to group1, Yes to group2
            d = 0  # No to both
            
            for _, row in pivot.iterrows():
                if pd.notna(row[groups[0]]) and pd.notna(row[groups[1]]):
                    if row[groups[0]] == most_common_response and row[groups[1]] == most_common_response:
                        a += 1
                    elif row[groups[0]] == most_common_response and row[groups[1]] != most_common_response:
                        b += 1
                    elif row[groups[0]] != most_common_response and row[groups[1]] == most_common_response:
                        c += 1
                    else:
                        d += 1
            
            # Create the contingency table
            contingency_table = np.array([[a, b], [c, d]])
            
            # McNemar's test statistic and p-value
            # For small sample sizes, we use the exact binomial test
            # For larger samples, we use the chi-square approximation
            if b + c < 25:
                # Use exact binomial test for small samples
                try:
                    # Try the newer scipy.stats.binomtest first (scipy >= 1.7.0)
                    try:
                        from scipy.stats import binomtest
                        result = binomtest(b, b + c, p=0.5)
                        p_value = result.pvalue
                    except ImportError:
                        # Fall back to the older binom_test for older scipy versions
                        p_value = stats.binom_test(b, b + c, p=0.5)
                    test_name = "mcnemar_exact"
                    test_stat = None
                except Exception as e:
                    logger.warning(f"Could not perform exact binomial test: {str(e)}")
                    # Fall back to chi-square approximation
                    test_stat = (b - c)**2 / (b + c) if b + c > 0 else 0
                    p_value = stats.chi2.sf(test_stat, 1)
                    test_name = "mcnemar_chi2"
            else:
                # Use chi-square approximation for larger samples
                test_stat = (b - c)**2 / (b + c) if b + c > 0 else 0
                p_value = stats.chi2.sf(test_stat, 1)
                test_name = "mcnemar_chi2"
            
            return {
                'test': test_name,
                'contingency_table': {
                    'both_yes': a,
                    'group1_yes_group2_no': b,
                    'group1_no_group2_yes': c,
                    'both_no': d
                },
                'test_statistic': test_stat,
                'p_value': p_value,
                'significant_at_0.05': p_value < 0.05
            }
        except Exception as e:
            logger.warning(f"Could not perform McNemar's test: {str(e)}")
            return None
    
    def perform_within_subjects_analysis(self, group_column='group', persona_column='persona_id'):
        """
        Perform a within-subjects analysis comparing responses across conditions.
        
        This method is specifically designed for experiments where the same personas
        respond to multiple conditions or questions (within-subjects design).
        
        Args:
            group_column (str): Column containing group or condition labels
            persona_column (str): Column containing persona identifiers
            
        Returns:
            dict: Dictionary containing analysis results
        """
        df = self.get_dataframe()
        
        if group_column not in df.columns or persona_column not in df.columns:
            logger.warning(f"Cannot perform within-subjects analysis: required columns not found")
            return None
        
        # Check if we have a proper within-subjects design
        persona_counts = df.groupby(persona_column).size()
        if (persona_counts > 1).sum() < 10:  # At least 10 personas should have multiple responses
            logger.warning("Few personas have multiple responses; this may not be a within-subjects design")
        
        # Calculate response distributions for each group
        group_distributions = {}
        for group, group_df in df.groupby(group_column):
            response_counts = group_df['response_value'].value_counts()
            response_percentages = response_counts / len(group_df) * 100
            
            group_distributions[group] = {
                'total_responses': len(group_df),
                'response_counts': response_counts.to_dict(),
                'response_percentages': response_percentages.to_dict()
            }
        
        # Perform McNemar's test for binary responses
        significance_result = self._perform_mcnemars_test(df, group_column, persona_column)
        
        # Calculate the number of personas who changed their response
        pivot = df.pivot_table(
            index=persona_column,
            columns=group_column,
            values='response_value',
            aggfunc='first'
        )
        
        # Count personas who changed their response between conditions
        changed_responses = 0
        total_paired = 0
        
        groups = df[group_column].unique()
        if len(groups) >= 2:
            for _, row in pivot.iterrows():
                if pd.notna(row[groups[0]]) and pd.notna(row[groups[1]]):
                    total_paired += 1
                    if row[groups[0]] != row[groups[1]]:
                        changed_responses += 1
        
        change_percentage = (changed_responses / total_paired * 100) if total_paired > 0 else 0
        
        return {
            'group_distributions': group_distributions,
            'significance_test': significance_result,
            'response_changes': {
                'total_paired_responses': total_paired,
                'changed_responses': changed_responses,
                'change_percentage': change_percentage
            }
        }
    
    def visualize(self, chart_type='bar', filepath=None):
        """
        Visualize the results.
        
        Args:
            chart_type (str): Type of chart to create ('bar', 'pie', etc.)
            filepath (str): Path to save the visualization (optional)
            
        Returns:
            matplotlib.figure.Figure: The created figure
        """
        try:
            import matplotlib.pyplot as plt
            
            df = self.get_dataframe()
            
            # For multiple choice questions
            if self.experiment_config.get('question_type') == 'multiple_choice':
                response_counts = df['response_value'].value_counts()
                
                fig, ax = plt.subplots(figsize=(10, 6))
                
                if chart_type == 'bar':
                    response_counts.plot(kind='bar', ax=ax)
                elif chart_type == 'pie':
                    response_counts.plot(kind='pie', ax=ax, autopct='%1.1f%%')
                else:
                    logger.warning(f"Unsupported chart type: {chart_type}")
                    return None
                
                plt.title(f"Responses to: {self.experiment_config.get('question', 'Survey Question')}")
                plt.tight_layout()
                
                if filepath:
                    plt.savefig(filepath)
                    logger.info(f"Saved visualization to {filepath}")
                
                return fig
            
            # For numeric responses
            elif self.experiment_config.get('question_type') == 'numeric':
                try:
                    df['response_value'] = pd.to_numeric(df['response_value'])
                    
                    fig, ax = plt.subplots(figsize=(10, 6))
                    
                    if chart_type == 'histogram':
                        df['response_value'].plot(kind='hist', ax=ax, bins=20)
                    elif chart_type == 'box':
                        df['response_value'].plot(kind='box', ax=ax)
                    else:
                        logger.warning(f"Unsupported chart type for numeric data: {chart_type}")
                        return None
                    
                    plt.title(f"Distribution of responses to: {self.experiment_config.get('question', 'Survey Question')}")
                    plt.tight_layout()
                    
                    if filepath:
                        plt.savefig(filepath)
                        logger.info(f"Saved visualization to {filepath}")
                    
                    return fig
                except:
                    logger.warning("Could not convert response values to numeric for visualization")
                    return None
            
            # Default case
            logger.warning("Unsupported question type for visualization")
            return None
        except ImportError:
            logger.error("Could not import matplotlib for visualization")
            return None
