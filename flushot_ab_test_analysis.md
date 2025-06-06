# Flu Shot A/B Test Analysis

## Overview
This analysis examines the results of an A/B test comparing the effectiveness of two messages encouraging flu shot uptake:
1. **Control (Standard Message)**: "Get your flu shot now! Will you get a flu shot?"
2. **Test (Social Proof Message)**: "4 of your neighbors have got a flushot. get yours now! Will you get a flu shot?"

The test was conducted with 50 personas from the PersonaHub dataset, with each persona answering both questions (within-subjects design). The temperature setting was reduced to 0.2 to ensure more consistent responses.

## Results Summary
- **Control Group (Standard Message)**: 76.0% responded "Yes" (38/50)
- **Test Group (Social Proof Message)**: 72.0% responded "Yes" (36/50)
- **Lift from social proof**: -5.3% (slight negative impact)

## Detailed Analysis

### Control Group Responses
The control group, which received the direct message without social proof, showed a high acceptance rate of 76.0%. This group included:
- 38 personas who responded "Yes"
- 12 personas who responded "No"

The "Yes" responses came from a diverse range of personas, with particularly strong acceptance among those with scientific, medical, or technical backgrounds.

### Test Group Responses
The test group, which received the social proof message, showed a slightly lower acceptance rate of 72.0%. This group included:
- 36 personas who responded "Yes"
- 14 personas who responded "No"

### Gender Analysis
- **Control Group**: 83.3% of males (15/18) and 100% of females (2/2) responded "Yes"
- **Test Group**: 72.2% of males (13/18) and 100% of females (2/2) responded "Yes"

### Unexpected Results
Contrary to our initial hypothesis, the social proof message performed slightly worse than the standard message, with a negative lift of -5.3%. While this difference is much smaller than in our previous test (-42.9%), it still suggests that social proof might not be as effective as expected for this particular scenario.

## Possible Explanations

### 1. Message Framing
The social proof message might be perceived as slightly manipulative by some personas, potentially triggering resistance. The phrasing "4 of your neighbors" might seem arbitrary or insufficient to create a strong social proof effect.

### 2. Within-Subjects Design Effects
Since each persona answered both questions, there may have been some carryover effects. Personas might have been consistent with their first answer when presented with the second question, regardless of the message framing.

### 3. Reduced Temperature Setting
Using a lower temperature setting (0.2) may have resulted in more consistent responses that were less influenced by the specific wording of the messages.

### 4. Persona Characteristics
The personas in our sample may have strong pre-existing opinions about flu shots that are not easily influenced by social proof. Many of the personas have scientific or medical backgrounds, which might make them more likely to base their decisions on their own knowledge rather than social influence.

## Statistical Significance Testing

We implemented McNemar's test for statistical significance, which is appropriate for within-subjects designs where the same personas answer both questions. This test specifically examines whether the changes in responses between conditions are statistically significant.

McNemar's test focuses on the discordant pairs - cases where a persona changed their response between conditions:
- Personas who answered "Yes" to control but "No" to test message
- Personas who answered "No" to control but "Yes" to test message

The test determines whether these changes are likely due to chance or represent a real effect of the different messages.

For small samples (discordant pairs < 25), we use the exact binomial test version of McNemar's test. For larger samples, we use the chi-square approximation.

### Implementation Details

We've integrated this statistical testing directly into the socialsim package by:

1. Adding a `_perform_mcnemars_test` method to the ResultsCollector class
2. Creating a new `perform_within_subjects_analysis` method for comprehensive analysis of within-subjects designs
3. Updating the `compare_groups` method to automatically detect and handle within-subjects designs

This implementation makes statistical significance testing available to all users of the package, not just for this specific A/B test.

## Limitations
- While larger than our previous test, the sample size (50 personas) is still relatively small
- The within-subjects design may introduce carryover effects
- The personas are fictional and may not perfectly represent real human decision-making
- The personas are predominantly from academic or professional backgrounds, which may not represent the general population
- Network connectivity issues may affect the ability to load personas from the PersonaHub dataset

## Recommendations for Future Tests
1. **Test different social proof formulations**: Try different formulations of social proof (e.g., "80% of people like you" or "Most healthcare professionals" instead of "4 of your neighbors")
2. **Between-subjects design with larger groups**: Use a pure between-subjects design with larger groups to avoid carryover effects
3. **Segment analysis**: Analyze results by persona type (e.g., scientists vs. historians) to see if social proof works differently for different groups
4. **Test different health behaviors**: Explore whether social proof is more effective for other health behaviors beyond flu shots
5. **Vary the strength of social proof**: Test different numbers (e.g., "2 of your neighbors" vs. "8 of your neighbors") to see if the strength of social proof matters

## Conclusion
This A/B test with 50 personas showed a slight negative impact (-5.3%) of social proof on flu shot acceptance. While the difference is not dramatic, it suggests that simple social proof messages may not always be effective for increasing flu shot uptake, particularly among highly educated or specialized individuals.

The high baseline acceptance rate in both groups (72-76%) indicates that most personas were already inclined to get a flu shot, which may have created a ceiling effect that limited the potential impact of the social proof message.

These results highlight the importance of carefully testing persuasive messages before deploying them at scale, as intuitive techniques like social proof may not always work as expected in all contexts or with all audiences.
