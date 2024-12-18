import os
import shutil
from abc import ABC, abstractmethod
from typing import List

class IFileExplorer(ABC):
    @abstractmethod
    def get_current_directory(self) -> str:
        pass

    @abstractmethod
    def set_current_directory(self, path: str) -> None:
        pass

    @abstractmethod
    def list_directory_contents(self) -> List[str]:
        pass

    @abstractmethod
    def navigate_to_index(self, index: int) -> None:
        pass

    @abstractmethod
    def go_to_parent_directory(self) -> None:
        pass


class IFileSelector(ABC):
    @abstractmethod
    def load_directory_contents(self) -> List[str]:
        pass

    @abstractmethod
    def select_files_by_indices(self, indices: List[int]) -> List[str]:
        pass

    @abstractmethod
    def get_selected_files(self) -> List[str]:
        pass

    @abstractmethod
    def clear_selection(self) -> None:
        pass


class IFileManager(ABC):
    @abstractmethod
    def copy_files(self, destination: str) -> None:
        pass

    @abstractmethod
    def move_files(self, destination: str) -> None:
        pass

    @abstractmethod
    def delete_files(self) -> None:
        pass


class FileExplorer(IFileExplorer):
    def __init__(self, start_path: str = None):
        self._current_path = start_path or os.path.expanduser('~')

    def get_current_directory(self) -> str:
        return self._current_path

    def set_current_directory(self, path: str) -> None:
        self._current_path = path

    def list_directory_contents(self) -> List[str]:
        return os.listdir(self._current_path)

    def navigate_to_index(self, index: int) -> None:
        contents = self.list_directory_contents()
        if index < 0 or index >= len(contents):
            raise ValueError("Invalid index.")
        selected = contents[index]
        full_path = os.path.join(self._current_path, selected)
        if os.path.isdir(full_path):
            self._current_path = full_path
        else:
            raise NotADirectoryError(f"{selected} is not a directory.")

    def go_to_parent_directory(self) -> None:
        parent = os.path.dirname(self._current_path)
        self._current_path = parent


class FileSelector(IFileSelector):
    def __init__(self, explorer: IFileExplorer):
        self._explorer = explorer
        self._selected_files = []
        self._current_directory_contents = []

    def load_directory_contents(self) -> List[str]:
        self._current_directory_contents = self._explorer.list_directory_contents()
        return self._current_directory_contents

    def select_files_by_indices(self, indices: List[int]) -> List[str]:
        self.load_directory_contents()
        current_dir = self._explorer.get_current_directory()
        self._selected_files.clear()

        for i in indices:
            if 0 <= i < len(self._current_directory_contents):
                full_path = os.path.join(current_dir, self._current_directory_contents[i])
                self._selected_files.append(full_path)
            else:
                raise ValueError("File index out of range.")

        return self._selected_files

    def get_selected_files(self) -> List[str]:
        return self._selected_files

    def clear_selection(self) -> None:
        self._selected_files.clear()


class FileManager(IFileManager):
    def __init__(self, selector: IFileSelector):
        self._selector = selector

    def copy_files(self, destination: str) -> None:
        files = self._selector.get_selected_files()
        for f in files:
            if os.path.exists(f):
                shutil.copy2(f, destination)
            else:
                raise FileNotFoundError(f"{f} does not exist.")
        self._selector.clear_selection()

    def move_files(self, destination: str) -> None:
        files = self._selector.get_selected_files()
        for f in files:
            if os.path.exists(f):
                shutil.move(f, destination)
            else:
                raise FileNotFoundError(f"{f} does not exist.")
        self._selector.clear_selection()

    def delete_files(self) -> None:
        files = self._selector.get_selected_files()
        for f in files:
            if os.path.isfile(f):
                os.remove(f)
            elif os.path.isdir(f):
                shutil.rmtree(f)
            else:
                raise FileNotFoundError(f"{f} does not exist.")
        self._selector.clear_selection()


def display_directory_contents(explorer: IFileExplorer) -> None:
    try:
        contents = explorer.list_directory_contents()
        print(f"\nCurrent Directory: {explorer.get_current_directory()}")
        print("-" * 50)
        for index, element in enumerate(contents):
            full_path = os.path.join(explorer.get_current_directory(), element)
            element_type = "📁 Folder" if os.path.isdir(full_path) else "📄 File"
            print(f"{index}. {element_type}: {element}")
    except PermissionError:
        print("Access denied to this directory.")
    except Exception as e:
        print(f"Error: {e}")


def main_menu():
    explorer = FileExplorer()
    selector = FileSelector(explorer)
    manager = FileManager(selector)

    while True:
        print("\n--- File Explorer ---")
        print("1. Display Directory")
        print("2. Navigate into a Subdirectory")
        print("3. Go to Parent Directory")
        print("4. Select Files")
        print("5. Copy Selected")
        print("6. Move Selected")
        print("7. Delete Selected")
        print("8. Quit")

        choice = input("Your choice: ").strip()
        
        try:
            if choice == '1':
                display_directory_contents(explorer)

            elif choice == '2':
                display_directory_contents(explorer)
                index = int(input("Enter navigation index: ").strip())
                explorer.navigate_to_index(index)
                display_directory_contents(explorer)

            elif choice == '3':
                explorer.go_to_parent_directory()
                display_directory_contents(explorer)

            elif choice == '4':
                display_directory_contents(explorer)
                indices_str = input("Enter file indices to select (comma-separated): ").strip()
                indices = [int(i) for i in indices_str.split(',')]
                selected = selector.select_files_by_indices(indices)
                print("Selected files:")
                for f in selected:
                    print(f" - {os.path.basename(f)}")

            elif choice == '5':
                dest = input("Enter destination path for copying: ").strip()
                manager.copy_files(dest)
                print("Files copied.")

            elif choice == '6':
                dest = input("Enter destination path for moving: ").strip()
                manager.move_files(dest)
                print("Files moved.")

            elif choice == '7':
                manager.delete_files()
                print("Files deleted.")

            elif choice == '8':
                print("Goodbye!")
                break

            else:
                print("Invalid choice. Please try again.")

        except Exception as e:
            print(f"An error occurred: {e}")


if __name__ == "__main__":
    main_menu()
