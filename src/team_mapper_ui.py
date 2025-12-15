"""
Interactive Team Mapper
Simple utility to assign people to teams using keyboard input
"""

import pandas as pd
import json
from pathlib import Path


def load_existing_mapping(mapping_path="team_mapping.json"):
    """Load existing team mapping"""
    with open(mapping_path, 'r') as f:
        return json.load(f)


def get_unmapped_people(data_path, mapping):
    """Get list of people not yet assigned to teams"""
    df = pd.read_csv(data_path)

    # Get all people in enablement categories
    enablement_cats = mapping['enablement_categories']
    enablement_df = df[df['categories'].isin(enablement_cats)]
    all_people = set(enablement_df['activity name'].unique())

    # Get already mapped people
    mapped_people = set()
    for team, people in mapping['teams'].items():
        mapped_people.update(people)

    # Return unmapped people, sorted
    unmapped = all_people - mapped_people
    return sorted(unmapped)


def save_mapping(mapping, mapping_path="team_mapping.json"):
    """Save the updated mapping"""
    with open(mapping_path, 'w') as f:
        json.dump(mapping, f, indent=2)
    print(f"\n✓ Saved to {mapping_path}")


def interactive_mapper():
    """Run the interactive team mapper"""
    data_path = r"data\stt_records_automatic.csv"
    mapping_path = "team_mapping.json"

    # Load data
    mapping = load_existing_mapping(mapping_path)
    unmapped_people = get_unmapped_people(data_path, mapping)

    if not unmapped_people:
        print("All people are already mapped to teams!")
        return

    # Get team list
    teams = list(mapping['teams'].keys())

    print("=" * 60)
    print("INTERACTIVE TEAM MAPPER")
    print("=" * 60)
    print(f"\nTotal unmapped people: {len(unmapped_people)}")
    print("\nAvailable teams:")
    for i, team in enumerate(teams, 1):
        print(f"  {i}. {team}")
    print(f"  s. Skip this person")
    print(f"  n. Create new team")
    print(f"  q. Quit and save")
    print()

    # Process each person
    for person in unmapped_people:
        print("-" * 60)
        print(f"\nPerson: {person}")

        while True:
            choice = input("Select team (1-{}, s, n, q): ".format(len(teams))).strip().lower()

            if choice == 'q':
                save_mapping(mapping, mapping_path)
                print(f"\nRemaining unmapped: {len(unmapped_people[unmapped_people.index(person):])}")
                return

            elif choice == 's':
                print(f"Skipped {person}")
                break

            elif choice == 'n':
                new_team = input("Enter new team name: ").strip()
                if new_team and new_team not in teams:
                    mapping['teams'][new_team] = []
                    teams.append(new_team)
                    print(f"Created team: {new_team}")
                    print("\nUpdated team list:")
                    for i, team in enumerate(teams, 1):
                        print(f"  {i}. {team}")
                continue

            elif choice.isdigit():
                team_idx = int(choice) - 1
                if 0 <= team_idx < len(teams):
                    selected_team = teams[team_idx]
                    mapping['teams'][selected_team].append(person)
                    print(f"✓ Assigned {person} to {selected_team}")
                    break
                else:
                    print("Invalid team number!")
            else:
                print("Invalid choice!")

    # Save at the end
    save_mapping(mapping, mapping_path)
    print("\n" + "=" * 60)
    print("ALL PEOPLE MAPPED!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        interactive_mapper()
    except KeyboardInterrupt:
        print("\n\nInterrupted! Progress has been saved.")
    except Exception as e:
        print(f"\nError: {e}")
