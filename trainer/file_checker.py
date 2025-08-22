import pickle
import os
import webbrowser

base_dir = os.path.abspath(os.path.dirname(__file__)) if "__file__" in globals() else os.getcwd()
training_data_dir = os.path.join(base_dir, "training_data")
os.makedirs(training_data_dir, exist_ok=True)
DATA_PATH = os.path.join(training_data_dir, "hand_positions.pkl")

def load_data(path=DATA_PATH):
    if not os.path.exists(path):
        return {}
    with open(path, "rb") as f:
        return pickle.load(f)


def save_data(data, path=DATA_PATH):
    with open(path, "wb") as f:
        pickle.dump(data, f)


def show_poses(data, allow_view=False):
    if not data:
        print("\nNo poses found in the dataset.\n")
        return

    print("\nAvailable poses:")
    for i, (pose, samples) in enumerate(data.items()):
        print(f"{i}: {pose} -> {len(samples)} samples")

    # Only prompt to view a sample when allow_view is True
    if not allow_view:
        return

    view = input("\nWould you like to view a sample from any pose? (y/n): ").strip().lower()
    if view == "y":
        try:
            idx = int(input("Enter pose index: "))
            if idx < 0 or idx >= len(data):
                print("Invalid index")
                return
            sample_idx = int(input("Enter sample number (0-based): "))
            key = list(data.keys())[idx]
            samples = data[key]
            if sample_idx < 0 or sample_idx >= len(samples):
                print("Invalid sample number")
                return
            print(f"\nSample from '{key}' (sample #{sample_idx}):")
            print(samples[sample_idx])
            print(f"No. of handmarks: {len(samples[sample_idx])}\n")
        except ValueError:
            print("Input must be an integer.")


def fix_poses(data):
    """Apply the logic:
    - Remove any pose with fewer than 100 samples
    - Trim any pose with more than 100 samples by removing excess entries from the front
    """
    if not data:
        print("\nNo poses to fix.\n")
        return data

    to_delete = [pose for pose, samples in data.items() if len(samples) < 100]
    to_trim = {pose: (len(samples) - 100) for pose, samples in data.items() if len(samples) > 100}

    if not to_delete and not to_trim:
        print("\nAll poses already have exactly 100 samples. Nothing to do.\n")
        return data

    print("\nThe following changes will be made:")
    if to_delete:
        print("\nPoses to be deleted (have < 100 samples):")
        for p in to_delete:
            print(f" - {p}: {len(data[p])} samples")
    if to_trim:
        print("\nPoses to be trimmed to 100 samples (will remove from the front):")
        for p, extra in to_trim.items():
            print(f" - {p}: remove {extra} entries -> {len(data[p]) - extra} remain")

    confirm = input("\nProceed with these changes? (y/n): ").strip().lower()
    if confirm != "y":
        print("Aborted. No changes made.")
        return data

    # Delete poses with fewer than 100 samples
    for p in to_delete:
        del data[p]

    # Trim poses with more than 100 samples (remove from front)
    for p, extra in to_trim.items():
        data[p] = data[p][extra:]

    save_data(data)
    print("\nFix applied and dataset saved.\n")
    return data


def remove_pose_by_index(data):
    if not data:
        print("\nNo poses to remove.\n")
        return data

    # Show poses but do not prompt to view a sample here
    show_poses(data, allow_view=False)
    try:
        idx = int(input("Enter the index of the pose to remove: "))
    except ValueError:
        print("Index must be an integer.")
        return data

    if idx < 0 or idx >= len(data):
        print("Invalid index")
        return data

    key = list(data.keys())[idx]
    confirm = input(f"Are you sure you want to delete '{key}' (type 'yes' to confirm)? ").strip().lower()
    if confirm == "yes":
        del data[key]
        save_data(data)
        print(f"Deleted '{key}' and saved dataset.\n")
    else:
        print("Aborted. No changes made.\n")
    return data


def clear_all(data):
    if not data:
        print("\nDataset already empty.\n")
        return {}
    confirm = input("Type CLEAR (all caps) to permanently remove ALL poses: ")
    if confirm == "CLEAR":
        data = {}
        save_data(data)
        print("All poses removed and dataset saved.\n")
    else:
        print("Aborted. No changes made.\n")
    return data


def open_colab_from_github_and_exit():
    # GitHub-hosted notebook — Colab will open it directly
    colab_url = "https://colab.research.google.com/github/DevashishHarsh/OpenCV-HandBot/blob/main/Train_Hand_Model.ipynb"
    try:
        webbrowser.open(colab_url, new=2)  # new tab if possible
        print("\nOpened the training notebook in Google Colab. The script will now exit.\n")
    except Exception:
        print("\nFailed to open the browser automatically.")
        print("Open Colab manually at:")
        print(colab_url)
    # Exit the script after attempting to open Colab
    exit(0)


def main():
    data = load_data()

    menu = ("\n-------------Model Checks-----------------\n"
            "1. Show (Shows the current poses with their names and sample counts)\n"
            "2. Fix (Fix them using the logic: delete <100, trim >100)\n"
            "3. Remove (Remove a certain pose by its index)\n"
            "4. Clear all (Removes all poses from the file)\n"
            "5. Train (Open the GitHub notebook in Colab and exit)\n"
            "0. Exit\n")

    while True:
        print(menu)
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            # When user explicitly chooses Show, allow viewing a sample
            show_poses(data, allow_view=True)
        elif choice == "2":
            data = fix_poses(data)
        elif choice == "3":
            data = remove_pose_by_index(data)
        elif choice == "4":
            data = clear_all(data)
        elif choice == "5":
            open_colab_from_github_and_exit()
            break
        elif choice == "0":
            print("Exiting.\n")
            break
        else:
            print("Invalid option. Please enter 0-5.")


if __name__ == "__main__":
    main()
