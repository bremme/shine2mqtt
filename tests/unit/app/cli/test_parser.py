from shine2mqtt.app.cli.parser import ArgParser


def test_sim_subcommand_enables_simulated_client() -> None:
    args = ArgParser().parse(["sim"])
    assert args.subcommand == "sim"
    assert args.simulated_client__enabled is True


def test_run_subcommand_disables_simulated_client() -> None:
    args = ArgParser().parse(["run"])
    assert args.subcommand == "run"
    assert args.simulated_client__enabled is False
