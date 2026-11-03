def get_int_input(prompt: str, min_val: int = None, max_val: int = None) -> int:
    while True:
       raw = input(prompt).strip()
       if not raw:
           print("Błąd: Pusta wartość. Spróbuj ponownie.")
           continue
       try:
           val = int(raw)
           if min_val is not None and val < min_val:
               print(f"Błąd: Wartość musi być większa lub równa {min_val}. Spróbuj ponownie.")
               continue
           if max_val is not None and val > max_val:
               print(f"Błąd: Wartość musi być mniejsza lub równa {max_val}. Spróbuj ponownie.")
               continue
           return val
       except ValueError:
            print("Błąd: Nieprawidłowe dane. Wprowadź liczbę całkowitą.")

def get_non_empty_string(prompt: str) -> str:
    while True:
        raw = input(prompt).strip()
        if not raw:
            print("Błąd: Pole tekstowe nie może być puste. Spróbuj ponownie.")
            continue
        return raw