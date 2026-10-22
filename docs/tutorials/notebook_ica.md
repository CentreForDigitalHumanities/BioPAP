# ICA Example

Independent Component Analysis (ICA) requires visual inspection and manual adjustments for each data file, so it is not included in the pipeline. The example notebook lets you run ICA on your own data and adjust variables to your needs.

## Using ICA with the pipeline

To use ICA as part of preprocessing, run the pipeline in two stages, with ICA between them:

1. Run preprocessing up to the point where you want to apply ICA, then save the output. You can process multiple files in batch.
2. Run the [ICA example notebook](https://github.com/CentreForDigitalHumanities/BioPAP/blob/main/examples/example_ICA.ipynb) on the saved files. It saves cleaned files and an ICA object containing the settings used, including the excluded components, for reproducibility.
3. Resume the pipeline using the ICA-cleaned files as input. This stage can also be run in batch.
