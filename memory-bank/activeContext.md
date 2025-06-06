# Active Context: SelfPlay

## Current Work Focus

The SelfPlay project is currently expanding its capabilities with the addition of social simulation features. The primary focus areas are:

1. **Social Simulation (SocialSim)**: Implementing a framework for conducting social science experiments with simulated personas, including surveys, A/B tests, and multivariate experiments.

2. **Persona Management**: Creating and managing a database of diverse personas for use in social simulations.

3. **Statistical Analysis**: Developing tools for analyzing the results of social experiments, including statistical tests and visualizations.

4. **Package Stability**: Ensuring the core functionality works reliably across different use cases and scenarios.

5. **Documentation**: Improving documentation to make the package more accessible to new users and contributors.

## Recent Changes

1. **SocialSim Module Implementation**: Added a new module for conducting social science experiments with simulated personas, including:
   - PersonaDB: A database for managing and sampling personas
   - ExperimentRunner: A framework for running experiments with personas
   - ResultsCollector: Tools for collecting, analyzing, and visualizing experiment results

2. **Multivariate Experiment Framework**: Implemented a framework for testing multiple message variants with the same set of personas, including:
   - Randomized message order to control for order effects
   - Comprehensive data collection of persona attributes and responses
   - Statistical analysis using Cochran's Q test and McNemar's test

3. **A/B Testing Capabilities**: Added support for A/B testing with control and test groups, including statistical significance testing.

4. **Auto-End Feature Implementation**: Added functionality to automatically detect when a conversation has naturally concluded, rather than requiring a fixed number of turns.

## Next Steps

1. **Expand SocialSim Capabilities**:
   - Add support for more complex experimental designs (factorial, repeated measures)
   - Implement more advanced statistical analyses
   - Create additional visualization options for experiment results
   - Develop tools for persona clustering and segmentation

2. **Persona Database Expansion**:
   - Increase the diversity and number of available personas
   - Add support for custom persona creation and import
   - Implement more sophisticated persona sampling strategies

3. **Enhanced Error Handling**: Improve error handling for edge cases, particularly around API failures and token limits.

4. **Performance Optimization**: Identify and address any performance bottlenecks, particularly for large-scale experiments.

5. **Documentation Improvements**: Create more detailed API documentation and usage examples for the SocialSim module.

6. **Integration with External Tools**: Add support for exporting results to common data analysis tools and formats.

## Active Decisions and Considerations

1. **API Provider Flexibility**: The system now supports multiple providers including AWS Bedrock (Claude), but further expansion to other providers would be beneficial.

2. **Persona Representation**: The current persona representation is text-based. Future considerations include more structured persona attributes and potentially using embeddings for more nuanced persona selection.

3. **Experiment Design Flexibility**: The current implementation supports basic experimental designs. More complex designs like factorial experiments or repeated measures could be added.

4. **Statistical Analysis Depth**: Current statistical analyses include basic tests like Cochran's Q and McNemar's. More advanced analyses could be implemented for more complex experimental designs.

5. **Memory Management**: For large-scale experiments with many personas, a more robust storage solution might be needed to manage the results efficiently.

6. **Template Management**: The current template system uses a static dictionary. A more dynamic approach might be beneficial for user-defined templates.

7. **Result Export Formats**: Currently supports CSV and JSON export. Additional formats or direct integration with data analysis tools might be useful.

## Important Patterns and Preferences

1. **Code Organization**: The project follows a modular approach with clear separation of concerns between modules:
   - Chatbot, RolePlay, and Templates for core conversation functionality
   - PersonaDB, ExperimentRunner, and ResultsCollector for social simulation

2. **Error Handling**: Comprehensive try-except blocks are used to catch and log errors, particularly around API calls and file operations.

3. **Configuration Management**: Environment variables are used for API configuration, making it easy to deploy in different environments.

4. **Memory Structure**: Conversation memory is structured as a list of role-content pairs, following the format expected by the OpenAI API.

5. **Method Naming**: Private methods are prefixed with underscore (_), following Python conventions.

6. **Data Collection**: Comprehensive data collection is emphasized in experiments, capturing all relevant attributes and metadata.

7. **Statistical Rigor**: Statistical tests are implemented with appropriate corrections for multiple comparisons.

## Learnings and Project Insights

1. **API Integration Challenges**: Working with external APIs requires robust error handling and consideration of rate limits and token constraints. The addition of AWS Bedrock support highlighted the importance of provider-agnostic abstractions.

2. **Conversation Flow Management**: Managing the flow of multi-turn conversations requires careful tracking of context and turn order.

3. **Template Design**: Creating effective templates requires balancing flexibility with ease of use.

4. **Memory Management Trade-offs**: In-memory storage provides speed but limits persistence, while file-based storage offers persistence but adds complexity.

5. **User Experience Considerations**: Even for a developer-focused tool, the API design significantly impacts the user experience.

6. **Experimental Design Complexity**: Designing social science experiments requires careful consideration of statistical power, randomization, and potential confounding variables.

7. **Persona Variability**: Different personas respond differently to the same messages, highlighting the importance of diverse persona sampling for robust experiments.

8. **Statistical Analysis Challenges**: Implementing statistical tests requires careful consideration of assumptions and appropriate corrections for multiple comparisons.

9. **Data Collection Importance**: Comprehensive data collection is crucial for meaningful analysis, including persona attributes, response times, and experimental conditions.
