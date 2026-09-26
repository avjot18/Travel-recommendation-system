from app.data_pipeline.cleaner import HTMLFileCleaner


INPUT_FILE = (
    "data/raw/manali/manali.html"
)

OUTPUT_FILE = (
    "data/cleaned/manali/incredible_india_manali.txt"
)


cleaner = HTMLFileCleaner()

cleaner.clean_file(
    input_path=INPUT_FILE,
    output_path=OUTPUT_FILE
)