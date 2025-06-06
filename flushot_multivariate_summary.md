# Flu Shot Multivariate Messaging Experiment Summary

## Overview

This experiment tests the effectiveness of 7 different message framings for encouraging flu shot uptake:

1. **Control (Direct)**: "Get your flu shot now! Will you get a flu shot?"
2. **Social Proof**: "78% of people in your community have already gotten their flu shot this season. Will you get a flu shot?"
3. **Authority**: "Medical experts at the CDC and WHO strongly recommend getting a flu shot this season. Will you get a flu shot?"
4. **Scarcity/Urgency**: "Flu vaccine supplies are limited this year and appointments are filling up quickly. Will you get a flu shot?"
5. **Personal Benefit**: "Getting a flu shot reduces your personal risk of illness by up to 60% and can prevent severe symptoms even if you do catch the flu. Will you get a flu shot?"
6. **Fear Appeal**: "Without a flu shot, you're at higher risk of hospitalization or even death from influenza, which kills thousands each year. Will you get a flu shot?"
7. **Reciprocity/Community Benefit**: "By getting a flu shot, you help protect vulnerable people in your community who cannot get vaccinated, such as infants and those with compromised immune systems. Will you get a flu shot?"

Each message applies a different persuasion principle from social psychology to flu shot uptake messaging.

## Experiment Design

- **Participants**: 50 standard personas from PersonaHub
- **Design**: Within-subjects (each persona responds to all 7 messages)
- **Randomization**: Message order randomized for each persona to control for order effects
- **Response Options**: Binary "Yes"/"No" to "Will you get a flu shot?"
- **Statistical Analysis**: Cochran's Q test for overall differences, post-hoc McNemar's tests for pairwise comparisons

## Test Run Results

We conducted a small test run with 5 personas and 3 message variants:

| Message Variant | Yes Responses | Percentage |
|----------------|---------------|------------|
| Control (Direct) | 3/5 | 60.0% |
| Authority | 4/5 | 80.0% |
| Fear Appeal | 3/5 | 60.0% |

**Cochran's Q Test Results**:
- Q statistic: 0.6667
- p-value: 0.7165
- Significant at α=0.05: No

The test run showed that the Authority message performed best (80% "Yes" responses), but the differences between messages were not statistically significant (p = 0.7165).

## Observations from Test Run

1. **Persona Variability**: Different personas responded differently to the same messages. For example:
   - The "school basketball team captain" responded "No" to both the Control and Fear Appeal messages, but "Yes" to the Authority message
   - The "divorced father of three" responded "No" to both the Control and Fear Appeal messages, but "Yes" to the Authority message
   - The "newly hired general counsel" and "engineer" responded "Yes" to all message variants

2. **Message Effectiveness**: The Authority message (citing CDC and WHO recommendations) was the most effective, with 80% "Yes" responses compared to 60% for the other messages.

3. **Response Consistency**: Some personas were consistent in their responses across all messages, while others varied depending on the message framing.

## Implementation Details

The experiment implementation includes:

1. **Comprehensive Data Collection**:
   - Full persona descriptions and attributes
   - Message details (variant, text, persuasion principle)
   - Response data (binary response, response time)
   - Message order (to analyze order effects)

2. **Statistical Analysis**:
   - Overall differences using Cochran's Q test
   - Pairwise comparisons using McNemar's test with Bonferroni correction
   - Demographic analysis by persona attributes

3. **Visualization**:
   - Bar chart showing "Yes" rates for each message variant
   - Color-coded by persuasion principle

## Next Steps

1. **Run Full Experiment**: Execute the full experiment with all 7 message variants and 50 personas
2. **Analyze Results**: Perform comprehensive statistical analysis including:
   - Overall differences between message variants
   - Pairwise comparisons between specific messages
   - Demographic patterns in responses
   - Order effects analysis

3. **Refine Messages**: Based on results, refine the most effective messages for further testing
4. **Test with Real Participants**: Validate findings with real human participants

## Technical Improvements

During development, we made several technical improvements to the experiment framework:

1. **Fixed DataFrame.applymap Deprecation**: Updated code to use DataFrame.map instead of the deprecated applymap method
2. **Implemented Custom Cochran's Q Test**: Added a custom implementation of Cochran's Q test for compatibility with different scipy versions
3. **Enhanced Error Handling**: Added robust error handling for statistical tests and API calls
4. **Randomized Message Order**: Implemented randomization of message order to control for order effects
5. **Comprehensive Data Logging**: Ensured all relevant data is captured for detailed analysis

## Conclusion

The multivariate experiment framework provides a powerful tool for testing different message framings for flu shot uptake. The test run suggests that Authority-based messages may be most effective, but a larger sample is needed for definitive conclusions. The full experiment with 50 personas and all 7 message variants will provide more robust insights into the effectiveness of different persuasion principles for flu shot messaging.
