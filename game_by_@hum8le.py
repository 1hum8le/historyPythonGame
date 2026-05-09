import json
import random
import sys
import os
import re
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text

console = Console()


def pobierz_sciezke_pliku(nazwa_pliku):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, nazwa_pliku)
    return os.path.join(os.path.abspath("."), nazwa_pliku)


class Game:
    def __init__(self):
        sciezka_json = pobierz_sciezke_pliku("data.json")
        try:
            with open(sciezka_json, "r", encoding="utf-8") as file:
                self.data = json.load(file)
            
            # TWORZYMY PUSTĄ LISTĘ NA WSZYSTKIE PYTANIA
            self.wszystkie_wydarzenia = []
            
            # PĘTLA PRZECHODZI PRZEZ WSZYSTKIE EPOKI I DODAJE JE DO GŁÓWNEJ LISTY
            for epoka in self.data["historia_daty"].values():
                self.wszystkie_wydarzenia.extend(epoka)
            
            self.dostepne_wydarzenia = list(self.wszystkie_wydarzenia)
            random.shuffle(self.dostepne_wydarzenia)
            
        except FileNotFoundError:
            console.print(f"[bold red]Błąd:[/bold red] Nie znaleziono pliku {sciezka_json}")
            input("Naciśnij Enter, aby zamknąć...")
            sys.exit(1)
        except KeyError:
            console.print("[bold red]Błąd:[/bold red] Nieprawidłowa struktura pliku JSON")
            input("Naciśnij Enter, aby zamknąć...")
            sys.exit(1)
            
    def losowe_wydarzenie(self):
        if not self.dostepne_wydarzenia:
            console.print(
                Panel(
                    "[bold cyan]Pula pytań została wyczerpana! Zaczynamy od nowa.[/bold cyan]",
                    border_style="cyan",
                )
            )
            self.dostepne_wydarzenia = list(self.wszystkie_wydarzenia)
            random.shuffle(self.dostepne_wydarzenia)

        self.wylosowane = self.dostepne_wydarzenia.pop()
        return self.wylosowane

    def generuj_opcje_abcd(self, prawidlowa_data):
        """
        Funkcja wyciąga rok z daty i generuje 3 fałszywe opcje (+/- 20 lat),
        a następnie je tasuje.
        """
        # Znajdujemy liczbę (rok) w tekście
        match = re.search(r"\d+", prawidlowa_data)
        if not match:
            # Zabezpieczenie na wypadek dziwnych formatów daty
            opcje = [prawidlowa_data, "Brak danych", "Nieznana data", "Błąd odczytu"]
            random.shuffle(opcje)
            slownik_opcji = {
                litera: opcja for litera, opcja in zip(["A", "B", "C", "D"], opcje)
            }
            return slownik_opcji, "A"

        rok = int(match.group())
        jest_pne = "p.n.e." in prawidlowa_data

        # Zbiór gwarantuje brak powtórzeń (zaczynamy od poprawnego roku)
        opcje_liczbowe = {rok}

        while len(opcje_liczbowe) < 4:
            # Generujemy przesunięcie o max 20 lat
            przesuniecie = random.randint(-20, 20)
            nowy_rok = rok + przesuniecie
            if nowy_rok > 0:  # Upewniamy się, że rok jest dodatni
                opcje_liczbowe.add(nowy_rok)

        # Przerabiamy liczby z powrotem na tekst z ewentualnym "p.n.e."
        opcje_tekstowe = []
        for r in opcje_liczbowe:
            if r == rok:
                opcje_tekstowe.append(prawidlowa_data)
            else:
                sufiks = " p.n.e." if jest_pne else ""
                opcje_tekstowe.append(f"{r}{sufiks}")

        # Tasujemy opcje i przypisujemy litery
        random.shuffle(opcje_tekstowe)
        slownik_opcji = {
            litera: opcja for litera, opcja in zip(["A", "B", "C", "D"], opcje_tekstowe)
        }

        # Odszukujemy, pod którą literą schowała się poprawna odpowiedź
        prawidlowa_litera = [
            klucz
            for klucz, wartosc in slownik_opcji.items()
            if wartosc == prawidlowa_data
        ][0]

        return slownik_opcji, prawidlowa_litera

    def main(self):
        console.clear()

        # --- MENU GŁÓWNE ---
        menu = Text(
            "Zagrajmy w Grę - Daty Historia\n", justify="center", style="bold magenta"
        )
        menu.append("\nWybierz poziom trudności:\n", style="white")
        menu.append("\n[1] Easy ", style="bold green")
        menu.append("- podpowiedź i wybór ABCD", style="white")
        menu.append("\n[2] Hard ", style="bold red")
        menu.append("- ręczne wpisywanie daty\n", style="white")
        menu.append("\n[q] Wyjście", style="gray")

        console.print(
            Panel(
                menu,
                title="[bold yellow]Menu Główne[/bold yellow]",
                border_style="magenta",
            )
        )

        wybor_trybu = Prompt.ask("Twój wybór", choices=["1", "2", "q"])
        if wybor_trybu == "q":
            sys.exit(0)

        tryb_easy = wybor_trybu == "1"
        numer_pytania = 0
        punkty = 0

        # --- GŁÓWNA PĘTLA GRY ---
        while True:
            console.clear()
            wydarzenie = self.losowe_wydarzenie()
            numer_pytania += 1

            console.print(
                f"[bold yellow]Pytanie numer: {numer_pytania} | Aktualne punkty: {punkty}[/bold yellow]\n"
            )

            if tryb_easy:
                # ================= TRYB EASY =================
                console.print(
                    Panel(
                        wydarzenie["ciekawostka"],
                        title="[bold blue]Podpowiedź (Szczegóły)[/bold blue]",
                        border_style="blue",
                    )
                )
                console.print(
                    f"[bold cyan]Wydarzenie:[/bold cyan] {wydarzenie['wydarzenie']}\n"
                )

                # Generowanie opcji A, B, C, D
                opcje, prawidlowa_litera = self.generuj_opcje_abcd(wydarzenie["data"])
                for litera, tekst in opcje.items():
                    console.print(f"  [bold magenta]{litera})[/bold magenta] {tekst}")

                podana_odpowiedz = Prompt.ask(
                    "\n[bold green]Wybierz poprawną odpowiedź[/bold green]",
                    choices=["a", "b", "c", "d", "q"],
                ).upper()

                if podana_odpowiedz == "Q":
                    sys.exit(0)

                if podana_odpowiedz == prawidlowa_litera:
                    console.print("\n[bold green]✅ Poprawna odpowiedź![/bold green]")
                    punkty += 1
                else:
                    console.print(
                        f"\n[bold red]❌ Błędna odpowiedź.[/bold red] Poprawny rok to: [bold white]{wydarzenie['data']} ({prawidlowa_litera})[/bold white]"
                    )

            else:
                # ================= TRYB HARD =================
                console.print(
                    f"[bold cyan]Wydarzenie:[/bold cyan] {wydarzenie['wydarzenie']}\n"
                )

                podana_odpowiedz = Prompt.ask(
                    "[bold green]Podaj prawidłowy rok wydarzenia[/bold green] (np. 44 p.n.e.)"
                ).strip()

                if podana_odpowiedz.lower() == "q":
                    sys.exit(0)

                if podana_odpowiedz == wydarzenie["data"]:
                    console.print("\n[bold green]✅ Poprawna odpowiedź![/bold green]")
                    punkty += 1
                else:
                    console.print(
                        f"\n[bold red]❌ Błędna odpowiedź.[/bold red] Poprawny rok to: [bold white]{wydarzenie['data']}[/bold white]"
                    )

                # W trybie Hard ciekawostka pojawia się PO odpowiedzi
                console.print(
                    Panel(
                        wydarzenie["ciekawostka"],
                        title="[bold blue]Szczegóły[/bold blue]",
                        border_style="blue",
                    )
                )

            input("\nNaciśnij Enter, aby przejść do następnego pytania...")

            # --- PODSUMOWANIE ---
            if numer_pytania % 20 == 0:
                console.clear()
                podsumowanie = f"Zdobyłeś [bold green]{punkty}[/bold green] punktów na [bold yellow]{numer_pytania}[/bold yellow] możliwych. Gratulacje!"
                console.print(
                    Panel(
                        podsumowanie,
                        title="[bold magenta]Podsumowanie[/bold magenta]",
                        border_style="green",
                    )
                )

                wybor = Prompt.ask("Czy grasz dalej?", choices=["t", "n"], default="t")
                if wybor == "n":
                    console.print(
                        "[bold cyan]Dzięki za grę! Do zobaczenia.[/bold cyan]"
                    )
                    break


if __name__ == "__main__":
    Game().main()
