from dataclasses import dataclass

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from app.data_pipeline.normalizer import (
    NormalizedBlock,
    NormalizedTemperature,
    NormalizedTransport,
)


class TemperatureModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    month: str
    minimum_celsius: float
    maximum_celsius: float

    def validate_values(self) -> None:
        if not -100 <= self.minimum_celsius <= 100:
            raise ValueError(
                "Minimum temperature is outside valid range."
            )

        if not -100 <= self.maximum_celsius <= 100:
            raise ValueError(
                "Maximum temperature is outside valid range."
            )

        if self.minimum_celsius > self.maximum_celsius:
            raise ValueError(
                "Minimum temperature cannot exceed maximum temperature."
            )


class TransportModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    transport_type: str
    value: str = Field(min_length=1)

    def validate_values(self) -> None:
        allowed_types = {
            "airport",
            "railway_station",
            "bus_station",
            "other",
        }

        if self.transport_type not in allowed_types:
            raise ValueError(
                f"Unsupported transport type: "
                f"{self.transport_type}"
            )


class KeyValueModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    key: str = Field(min_length=1)
    value: str = Field(min_length=1)


class NormalizedDataModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    block_type: str
    content: object


@dataclass
class ValidationResult:
    valid_blocks: list[NormalizedBlock]
    invalid_blocks: list[dict]

    @property
    def is_valid(self) -> bool:
        return len(self.invalid_blocks) == 0


class DataValidator:

    SUPPORTED_BLOCK_TYPES = {
        "temperature",
        "transport",
        "paragraph",
        "list",
        "key_value",
    }

    def validate(
        self,
        blocks: list[NormalizedBlock],
    ) -> ValidationResult:

        valid_blocks = []
        invalid_blocks = []

        for index, block in enumerate(blocks):

            try:
                self._validate_block(
                    block
                )

                valid_blocks.append(
                    block
                )

            except (
                ValueError,
                ValidationError,
                TypeError,
            ) as error:

                invalid_blocks.append(
                    {
                        "index": index,
                        "block_type": getattr(
                            block,
                            "block_type",
                            None,
                        ),
                        "content": getattr(
                            block,
                            "content",
                            None,
                        ),
                        "error": str(error),
                    }
                )

        return ValidationResult(
            valid_blocks=valid_blocks,
            invalid_blocks=invalid_blocks,
        )

    def _validate_block(
        self,
        block: NormalizedBlock,
    ) -> None:

        if not isinstance(
            block,
            NormalizedBlock,
        ):
            raise TypeError(
                "Block must be a NormalizedBlock."
            )

        if (
            block.block_type
            not in self.SUPPORTED_BLOCK_TYPES
        ):
            raise ValueError(
                f"Unsupported block type: "
                f"{block.block_type}"
            )

        if block.block_type == "temperature":
            self._validate_temperature(
                block.content
            )

        elif block.block_type == "transport":
            self._validate_transport(
                block.content
            )

        elif block.block_type == "paragraph":
            self._validate_paragraph(
                block.content
            )

        elif block.block_type == "list":
            self._validate_list(
                block.content
            )

        elif block.block_type == "key_value":
            self._validate_key_value(
                block.content
            )

    def _validate_temperature(
        self,
        content,
    ) -> None:

        if isinstance(
            content,
            NormalizedTemperature,
        ):
            model = TemperatureModel(
                month=content.month,
                minimum_celsius=(
                    content.minimum_celsius
                ),
                maximum_celsius=(
                    content.maximum_celsius
                ),
            )

        elif isinstance(
            content,
            dict,
        ):
            model = TemperatureModel(
                **content
            )

        else:
            raise TypeError(
                "Temperature content must be "
                "NormalizedTemperature or dict."
            )

        model.validate_values()

        valid_months = {
            "january",
            "february",
            "march",
            "april",
            "may",
            "june",
            "july",
            "august",
            "september",
            "october",
            "november",
            "december",
        }

        if model.month.lower() not in valid_months:
            raise ValueError(
                f"Invalid month: {model.month}"
            )

    def _validate_transport(
        self,
        content,
    ) -> None:

        if isinstance(
            content,
            NormalizedTransport,
        ):
            model = TransportModel(
                transport_type=(
                    content.transport_type
                ),
                value=content.value,
            )

        elif isinstance(
            content,
            dict,
        ):
            model = TransportModel(
                **content
            )

        else:
            raise TypeError(
                "Transport content must be "
                "NormalizedTransport or dict."
            )

        model.validate_values()

    def _validate_paragraph(
        self,
        content,
    ) -> None:

        if not isinstance(
            content,
            str,
        ):
            raise TypeError(
                "Paragraph content must be a string."
            )

        if not content.strip():
            raise ValueError(
                "Paragraph cannot be empty."
            )

    def _validate_list(
        self,
        content,
    ) -> None:

        if not isinstance(
            content,
            list,
        ):
            raise TypeError(
                "List content must be a list."
            )

        for item in content:

            if not isinstance(
                item,
                str,
            ):
                raise TypeError(
                    "Every list item must be a string."
                )

            if not item.strip():
                raise ValueError(
                    "List items cannot be empty."
                )

    def _validate_key_value(
        self,
        content,
    ) -> None:

        if isinstance(
            content,
            dict,
        ):
            KeyValueModel(
                **content
            )
            return

        raise TypeError(
            "Key-value content must be a dictionary."
        )


if __name__ == "__main__":

    from pathlib import Path

    from app.data_pipeline.dom_extractor import (
        DOMContentExtractor,
    )

    from app.data_pipeline.normalizer import (
        DataNormalizer,
    )

    input_path = Path(
        "data/raw/manali/manali.html"
    )

    html = input_path.read_text(
        encoding="utf-8",
        errors="ignore",
    )

    extractor = DOMContentExtractor()

    extracted_blocks = extractor.extract(
        html
    )

    normalizer = DataNormalizer()

    normalized_blocks = normalizer.normalize(
        extracted_blocks
    )

    validator = DataValidator()

    result = validator.validate(
        normalized_blocks
    )

    print(
        f"Normalized blocks: "
        f"{len(normalized_blocks)}"
    )

    print(
        f"Valid blocks: "
        f"{len(result.valid_blocks)}"
    )

    print(
        f"Invalid blocks: "
        f"{len(result.invalid_blocks)}"
    )

    if result.invalid_blocks:

        print(
            "\nVALIDATION ERRORS"
        )

        for error in result.invalid_blocks:

            print(
                "\n",
                error,
            )

    else:

        print(
            "\nVALIDATION PASSED"
        )