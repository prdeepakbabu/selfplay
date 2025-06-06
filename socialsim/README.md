# SocialSim: Social Science Experiment Simulation

SocialSim is an extension to the SelfPlay package that adds capabilities for conducting simulations of social science experiments. It enables researchers, marketers, policy makers, and educators to simulate surveys with large numbers of AI personas, conduct A/B testing, and analyze results with statistical metrics.

## Features

- **Persona Database**: Load and manage diverse personas from PersonaHub or other sources
- **Survey Experiments**: Run surveys with configurable questions and response options
- **A/B Testing**: Compare different question formulations to see how framing affects responses
- **Multi-Variant Testing**: Test multiple variants of a question simultaneously
- **Statistical Analysis**: Analyze results with descriptive and inferential statistics
  - **Within-Subjects Analysis**: McNemar's test for paired designs
  - **Between-Subjects Analysis**: Chi-square and t-tests for independent groups
- **Results Visualization**: Create charts and graphs to visualize experiment results
- **Data Export**: Export results to CSV or JSON for further analysis

## Installation

SocialSim is included with the SelfPlay package. To install the required dependencies:

```bash
pip install selfplay[socialsim]
```

Or install all dependencies:

```bash
pip install selfplay[all]
```

## Quick Start

```python
from selfplay.socialsim import PersonaHubDB, ExperimentRunner

# Load personas from PersonaHub with lazy loading (only loads personas when needed)
persona_db = PersonaHubDB(use_elite=True, use_standard=True, max_personas=500)

# Create experiment runner
runner = ExperimentRunner(persona_db)

# Run a simple survey
results = runner.run_survey(
    question="Do you support increasing the minimum wage to $15 per hour?",
    options=["Strongly support", "Support", "Neutral", "Oppose", "Strongly oppose"],
    n=100,  # Number of personas to sample
    provider="azure",  # LLM provider to use
    question_type="multiple_choice"
)

# Print summary statistics
stats = results.summary_statistics()
print("Response counts:", stats['response_counts'])
print("Response percentages:", stats['response_percentages'])

# Export results
results.export_csv("survey_results.csv")

# Visualize results
results.visualize(chart_type="bar", filepath="survey_results.png")
```

## Using AWS Bedrock with Claude 3.7

SocialSim supports using AWS Bedrock with Claude 3.7, which provides excellent performance for persona simulation:

```python
from selfplay.socialsim import PersonaHubDB, ExperimentRunner

# Load personas from PersonaHub with lazy loading
persona_db = PersonaHubDB(use_elite=True, use_standard=True, max_personas=500)

# Create experiment runner
runner = ExperimentRunner(persona_db)

# Run a simple survey with AWS Bedrock and Claude 3.7
results = runner.run_survey(
    question="Do you support increasing the minimum wage to $15 per hour?",
    options=["Strongly support", "Support", "Neutral", "Oppose", "Strongly oppose"],
    n=100,  # Number of personas to sample
    provider="aws",  # Use AWS Bedrock
    model="us.anthropic.claude-3-7-sonnet-20250219-v1:0",  # Claude 3.7 Sonnet model
    question_type="multiple_choice"
)
```

### AWS Credentials Setup

To use AWS Bedrock, you need to set up your AWS credentials. You can do this in several ways:

1. **Environment variables**:
   ```bash
   export AWS_ACCESS_KEY_ID=your_access_key
   export AWS_SECRET_ACCESS_KEY=your_secret_key
   export AWS_REGION=us-east-1  # or your preferred region
   ```

2. **AWS credentials file**:
   Create or edit `~/.aws/credentials`:
   ```
   [default]
   aws_access_key_id = your_access_key
   aws_secret_access_key = your_secret_key
   ```
   
   And `~/.aws/config`:
   ```
   [default]
   region = us-east-1  # or your preferred region
   ```

3. **Pass credentials directly**:
   ```python
   results = runner.run_survey(
       # ... other parameters ...
       provider="aws",
       model="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
       provider_kwargs={
           "aws_access_key": "your_access_key",
           "aws_secret_key": "your_secret_key",
           "region": "us-east-1"
       }
   )
   ```

## Running A/B Tests

### Between-Subjects Design (Independent Groups)

```python
from selfplay.socialsim import PersonaHubDB, ExperimentRunner

# Load personas with lazy loading
persona_db = PersonaHubDB(max_personas=500)

# Run an A/B test with between-subjects design (different personas in each group)
results = ExperimentRunner.ab_test(
    persona_db=persona_db,
    control_question="Would you support a carbon tax that increases energy costs by 10% but reduces pollution?",
    test_question="Would you support a clean energy investment that increases energy costs by 10% but creates new jobs?",
    options=["Strongly support", "Support", "Neutral", "Oppose", "Strongly oppose"],
    n=200,  # Total number of personas (split between control and test)
    provider="aws",  # Using AWS Bedrock
    model="us.anthropic.claude-3-7-sonnet-20250219-v1:0"  # Claude 3.7 Sonnet model
)

# Compare groups (automatically uses chi-square test for between-subjects design)
comparison = results.compare_groups()
print("Control group:", comparison['group_distributions']['control'])
print("Test group:", comparison['group_distributions']['test'])
print("Significance test:", comparison['significance_test'])
```

### Within-Subjects Design (Paired Responses)

```python
from selfplay.socialsim import PersonaHubDB, ExperimentRunner, ResultsCollector

# Load personas with lazy loading
persona_db = PersonaHubDB(max_personas=500)
runner = ExperimentRunner(persona_db)

# For within-subjects design, run two separate surveys with the same personas
# First, run the control question survey
control_results = runner.run_survey(
    question="Would you support a carbon tax that increases energy costs by 10% but reduces pollution?",
    options=["Strongly support", "Support", "Neutral", "Oppose", "Strongly oppose"],
    n=100,
    provider="aws",
    model="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
    group_name="control"
)

# Then, run the test question survey with the same personas
test_results = runner.run_survey(
    question="Would you support a clean energy investment that increases energy costs by 10% but creates new jobs?",
    options=["Strongly support", "Support", "Neutral", "Oppose", "Strongly oppose"],
    n=100,
    provider="aws",
    model="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
    group_name="test",
    use_personas=control_results.get_personas()  # Use the same personas as the control group
)

# Combine the results
combined_config = {
    "type": "ab_test",
    "control_question": control_results.responses[0].question_text,
    "test_question": test_results.responses[0].question_text,
    "options": control_results.responses[0].question_options,
    "question_type": control_results.responses[0].question_type,
}
combined_results = ResultsCollector(combined_config)

# Add all responses from both collectors
for response in control_results.responses:
    combined_results.add_response(response)
for response in test_results.responses:
    combined_results.add_response(response)
combined_results.finalize()

# Perform within-subjects analysis (uses McNemar's test for paired data)
analysis = combined_results.perform_within_subjects_analysis()
print("Group distributions:", analysis['group_distributions'])
print("Significance test:", analysis['significance_test'])
print("Response changes:", analysis['response_changes'])
```

## Running Multi-Variant Tests

```python
from selfplay.socialsim import PersonaHubDB, ExperimentRunner

# Load personas with lazy loading
persona_db = PersonaHubDB(max_personas=500)

# Run a multi-variant test
results = ExperimentRunner.multi_variant_test(
    persona_db=persona_db,
    base_question="How likely would you be to complete this online course?",
    variants={
        "video_lectures": "This course features 10 video lectures of 15 minutes each.",
        "interactive": "This course features 10 interactive modules with hands-on exercises.",
        "text_based": "This course features 10 in-depth reading assignments with quizzes.",
        "mixed_format": "This course features a mix of videos, readings, and interactive exercises."
    },
    options=["Very likely", "Somewhat likely", "Neutral", "Somewhat unlikely", "Very unlikely"],
    n=50,  # Number of personas per variant
    provider="azure"
)

# Compare variants
comparison = results.compare_groups(group_column="group")
print("Comparison:", comparison)
```

## Persona Sampling and Filtering

```python
# Sample personas randomly
personas = persona_db.sample(n=100)

# Sample personas stratified by gender
personas = persona_db.sample(n=100, stratify_by="gender")

# Sample personas with filtering
personas = persona_db.sample(
    n=100,
    filter_by={"gender": "female", "age": lambda x: x > 30}
)
```

## Enhancing Personas with LLMs

```python
# Extract structured attributes from persona descriptions using LLMs
persona_db.enhance_with_llm(provider="azure", model="gpt-4")
```

## Exporting Results

```python
# Export to CSV
results.export_csv("results.csv")

# Export to JSON
results.export_json("results.json")

# Get as pandas DataFrame
df = results.get_dataframe()
```

## Visualizing Results

```python
# Create a bar chart
results.visualize(chart_type="bar", filepath="bar_chart.png")

# Create a pie chart
results.visualize(chart_type="pie", filepath="pie_chart.png")

# For numeric data, create a histogram
results.visualize(chart_type="histogram", filepath="histogram.png")
```

## API Reference

### PersonaHubDB

```python
PersonaHubDB(use_elite=True, use_standard=True, cache_dir=None, max_personas=1000)
```

- `use_elite`: Whether to include elite_persona dataset
- `use_standard`: Whether to include standard persona dataset
- `cache_dir`: Directory to cache the dataset
- `max_personas`: Maximum number of personas to load (default: 1000)

The PersonaHubDB class uses lazy loading to optimize memory usage and download time. It only loads personas when needed, rather than downloading the entire dataset at initialization. This is particularly useful when working with the large PersonaHub dataset (16GB+).

### ExperimentRunner

```python
ExperimentRunner(persona_db)
```

- `persona_db`: PersonaDB instance

#### Methods

```python
run_survey(question, options, n=100, stratify_by=None, filter_by=None, provider="azure", model=None, question_type="multiple_choice")
```

```python
ab_test(persona_db, control_question, test_question, options, n=100, stratify_by=None, filter_by=None, provider="azure", model=None, question_type="multiple_choice")
```

```python
multi_variant_test(persona_db, base_question, variants, options, n=100, stratify_by=None, filter_by=None, provider="azure", model=None, question_type="multiple_choice")
```

### ResultsCollector

```python
ResultsCollector(experiment_config)
```

- `experiment_config`: Configuration of the experiment

#### Methods

```python
add_response(response)
```

```python
finalize()
```

```python
get_dataframe()
```

```python
export_csv(filepath)
```

```python
export_json(filepath)
```

```python
summary_statistics()
```

```python
compare_groups(group_column='group', paired=False, persona_column='persona_id')
```
- `group_column`: Column to group by
- `paired`: Whether to treat the data as paired (within-subjects design)
- `persona_column`: Column containing persona identifiers (for paired analysis)

```python
perform_within_subjects_analysis(group_column='group', persona_column='persona_id')
```
- `group_column`: Column containing group or condition labels
- `persona_column`: Column containing persona identifiers

```python
visualize(chart_type='bar', filepath=None)
```

## Statistical Testing

SocialSim provides built-in statistical testing for both between-subjects and within-subjects experimental designs:

### Between-Subjects Testing

For between-subjects designs (independent groups):
- **Categorical data**: Chi-square test of independence
- **Numeric data**: Independent samples t-test (2 groups) or ANOVA (3+ groups)

### Within-Subjects Testing

For within-subjects designs (paired responses):
- **Categorical data**: McNemar's test (for binary responses) or Cochran's Q test (for 3+ conditions)
  - For small samples (discordant pairs < 25), the exact binomial test is used
  - For larger samples, the chi-square approximation is used
- **Numeric data**: Paired samples t-test (2 conditions) or repeated measures ANOVA (3+ conditions)

The appropriate test is automatically selected based on the data type and experimental design.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
