from random import choice

simple_examples: list[str] = [
    "What is current price of Infosys?",
    "What was last closing price of Tata Motors?",
    "What is current price of VA Tech Wabag?",
    "What if current price of HCL Tech?",
]

analytical_examples: list[str] = [
    "What is current price of TCS and how has it change from previous market day?",
    "What is current price of Coal India and has it gone up or down in 1 month? Show with chart.",
    "What is current price of Tata Motors Passenger Vehicle against Commercial Vehicle?",
    "How has HCL Tech performed in last 3 months? Provide insight with full chart.",
]

trend_examples: list[str] = [
    "Give me list of 10 Stocks which are currently at their 52 week high.",
    "Give me list of 10 Stocks in Petrochemicals Sector.",
    "Give me list of 5 Stocks in Pharmaceutical Industry.",
    "Give me list of 5 Stocks operating in Information Technology Sector.",
    "Give me list of 5 stocks which have gained volume in this week.",
]


def format_example(exp: str) -> str:
    return f"{exp:^100}"


def strip_example(exp: str) -> str:
    return exp.strip().strip("ㅤ")


def get_examples() -> tuple[str, str, str]:
    return (
        format_example(choice(simple_examples)),
        format_example(choice(analytical_examples)),
        format_example(choice(trend_examples)),
    )
