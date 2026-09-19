#!/usr/bin/env python3
"""
PolarSync Simulation CLI - Entry Point
SIH 2026 Problem Statement: SIH26062
"""

import argparse
import os
import sys
from src.scenario_runner import ScenarioRunner
from src.alerts.formatters import format_alert_box


def main():
    parser = argparse.ArgumentParser(
        description="PolarSync: Integrated Polar Expedition Simulation Engine"
    )
    parser.add_argument(
        "--scenario",
        type=int,
        choices=[1, 2, 3, 4, 5],
        default=1,
        help="Scenario index to execute (1: Normal, 2: Fuel Crisis, 3: Emergency SAR, 4: Cargo Breach, 5: Offline Sync)"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Execute all 5 demonstration scenarios consecutively"
    )
    parser.add_argument(
        "--export-csv",
        type=str,
        default=None,
        help="Optional filepath to export telemetry log as CSV"
    )

    args = parser.parse_args()

    base_dir = os.path.dirname(os.path.abspath(__file__))
    base_config = os.path.join(base_dir, "configs", "base_environment.json")
    
    scenario_files = {
        1: os.path.join(base_dir, "configs", "scenarios", "scenario_1_normal.json"),
        2: os.path.join(base_dir, "configs", "scenarios", "scenario_2_fuel_crisis.json"),
        3: os.path.join(base_dir, "configs", "scenarios", "scenario_3_emergency_sar.json"),
        4: os.path.join(base_dir, "configs", "scenarios", "scenario_4_cold_chain_breach.json"),
        5: os.path.join(base_dir, "configs", "scenarios", "scenario_5_connectivity_loss.json")
    }

    scenarios_to_run = [1, 2, 3, 4, 5] if args.all else [args.scenario]

    for sc_idx in scenarios_to_run:
        scenario_path = scenario_files[sc_idx]
        runner = ScenarioRunner(base_config, scenario_path)
        result = runner.run(verbose=True)

        if result["alerts"]:
            print("\n" + "=" * 70)
            print(f"ALERTS GENERATED DURING SCENARIO {sc_idx} (Total: {len(result['alerts'])})")
            print("=" * 70)
            for alert in result["alerts"]:
                print(format_alert_box(alert))

        if args.export_csv:
            df = runner.export_telemetry_dataframe()
            if args.all:
                base_name, ext = os.path.splitext(args.export_csv)
                ext = ext if ext else ".csv"
                export_filename = f"{base_name}_scenario_{sc_idx}{ext}"
            else:
                export_filename = args.export_csv
            df.to_csv(export_filename, index=False)
            print(f"\n[Telemetry Export] Exported {len(df)} telemetry rows to: {export_filename}")


if __name__ == "__main__":
    main()
