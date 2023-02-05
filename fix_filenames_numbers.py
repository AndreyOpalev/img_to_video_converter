from enum import Enum
import re
import os


class States(Enum):
    SelectFolder = 1
    CheckFolderExist = 2
    ApproveFolder = 3
    Rename = 4
    Repeat = 5
    Error = 6


if __name__ == '__main__':
    print("Enter Ctrl-D or Ctrl-C to close the script.\n")

    state = States.SelectFolder

    while state != States.Error:
        if state == States.SelectFolder:
            path = input("Enter a full path to folder: ")
            state = States.CheckFolderExist
        elif state == States.CheckFolderExist:
            isExist = os.path.exists(path)
            if isExist:
                print("The first files in the folder:")
                parent_list = os.listdir(path)
                max_to_print = min(len(parent_list), 5)
                for i in range(0, max_to_print):
                    print(f"    {parent_list[i]}")
                state = States.ApproveFolder
            else:
                print("Folder does not exist.")
                state = States.SelectFolder
        elif state == States.ApproveFolder:
            approve = input("Is it correct folder (enter [y] or [n]): ")
            if approve == 'y':
                state = States.Rename
            elif approve == 'n':
                state = States.SelectFolder
        elif state == States.Rename:
            parent_list = os.listdir(path)
            print("Parent list size:", len(parent_list))
            for filename in parent_list:
                # find index
                found_digits = re.findall(r'\d+', filename)
                if len(found_digits) == 0:
                    print(f"Skipped: {filename}")
                    continue

                index_str = found_digits[-1]
                index = int(index_str)

                # Generate a new name
                search_res = re.search(index_str, filename)
                start_pos = search_res.start()
                end_pos = search_res.end()
                new_name = '{}{}{}'.format(filename[:start_pos],
                                           f"{index:04}",
                                           filename[end_pos:])

                # Rename
                old_name = os.path.join(path, filename)
                new_name = os.path.join(path, new_name)
                print(f" {old_name} --> {new_name}")
                os.rename(old_name, new_name)

            state = States.Repeat
        elif state == States.Repeat:
            repeat = input("Repeat? Enter [y] or [n]: ")
            if repeat == 'y':
                state = States.SelectFolder
            elif repeat == 'n':
                exit(1)

        else:
            print("Unexpected behaviour.")
            state = States.Error

    print("Error occurred. Terminating.")
    exit(0)
