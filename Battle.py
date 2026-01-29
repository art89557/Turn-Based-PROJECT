# battle.py
import os
import time

from entities import Character, Boss # Pastikan Boss diimport juga

class Battle:
    def __init__(self, player_team, boss):
        self.player_team = player_team
        self.boss = boss
        self.game_objects = self.player_team + [self.boss]
        self.turn_order = sorted(self.game_objects, key=lambda x: x.spd, reverse=True)
        self.skill_points = 3
        self.max_skill_points = 5

    def display_ui(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print("="*40)
        print("BATTLE STATUS")
        print("="*40)
        print(f"BOSS: {self.boss.name} | HP: {int(self.boss.hp)}/{int(self.boss.max_hp)}")
        print("----------------------------------------") # Changed to use consistent '-'
        print("PLAYER TEAM:")
        for i, char in enumerate(self.player_team):
            hp_bar = f"HP: {int(char.hp)}/{int(char.max_hp)}"
            energy_bar = f"Energy: {char.energy}/{char.max_energy}"
            status = "(K.O.)" if not char.is_alive else ""
            print(f"  [{i+1}] {char.name:<15} | {hp_bar:<20} | {energy_bar:<20} {status}")
        print("="*40)
        print(f"Skill Points: {self.skill_points}/{self.max_skill_points}")
        print("="*40)

    def start_battle(self):
        print("\nPertarungan dimulai!")
        while self.is_battle_active():
            self.process_turn()
            time.sleep(1) # Delay antar giliran agar lebih mudah diikuti
        self.end_battle()

    def is_battle_active(self):
        # Pertempuran berlanjut selama boss hidup DAN setidaknya ada satu pemain yang hidup
        return self.boss.is_alive and any(char.is_alive for char in self.player_team)

    def process_turn(self):
        for entity in list(self.turn_order): # Gunakan list() untuk menghindari masalah modifikasi selama iterasi
            if not self.is_battle_active(): # Cek kondisi menang/kalah setelah setiap aksi
                break
            
            if entity.is_alive:
                self.display_ui()
                print(f"\nGiliran {entity.name}!")
                entity.tick_status() # Proses status effect di awal giliran

                if isinstance(entity, Character):
                    self.handle_character_turn(entity)
                elif isinstance(entity, Boss):
                    self.handle_boss_turn(entity)
                
    def handle_character_turn(self, character):
        while True:
            self.display_ui()
            print(f"\n{character.name}'s Action:")
            print("[1] Basic Attack")
            print("[2] Skill")
            print("[3] Special")
            print("[4] Lihat Stat Karakter") # Opsi tambahan
            
            choice = input("Pilihan Aksi: > ")

            if choice == "1":
                # Karakter menyerang boss
                target = self.select_target(self.boss) # Hanya boss sebagai target
                if target:
                    character.basic_attack(target)
                    break
            elif choice == "2":
                if character.energy >= 20: # Contoh biaya skill
                    # Target skill bisa musuh atau teman, tergantung karakter
                    if character.role in ["DPS", "Sub-DPS", "Debuffer"]:
                        target = self.select_target(self.boss) # Skill ke boss
                    elif character.role in ["Healer", "Support", "Tank"]:
                        target = self.select_target(self.player_team) # Skill ke teman/diri sendiri
                    
                    if target:
                        if character.skill(target, team=self.player_team): # Pass team for AoE skills like Garen's Special
                            character.energy -= 20
                            break
                else:
                    print("Energi tidak cukup untuk Skill!")
            elif choice == "3":
                if character.energy >= character.max_energy:
                    # Target special bisa musuh atau teman, tergantung karakter
                    if character.role in ["DPS", "Sub-DPS", "Debuffer"]:
                        target = self.select_target(self.boss) # Special ke boss
                    elif character.role in ["Healer", "Support", "Tank"]:
                        target = self.select_target(self.player_team) # Special ke teman/diri sendiri

                    if target:
                        if character.special(target, team=self.player_team): # Pass team for AoE skills like Garen's Special
                            break
                else:
                    print("Energi tidak cukup untuk Special!")
            elif choice == "4":
                for char in self.player_team:
                    char.display_details()
                input("\nTekan Enter untuk kembali...")
                self.display_ui() # Redraw UI
            else:
                print("Pilihan tidak valid.")

    def handle_boss_turn(self, boss):
        # Boss selalu menyerang player_team
        boss.decide_action(self.player_team) # Logic AI boss untuk memilih target dari player_team

    def select_target(self, available_targets):
        """
        Memilih target dari daftar yang tersedia.
        Jika available_targets adalah objek tunggal (misal, boss), langsung kembalikan.
        Jika list (misal, player_team), tampilkan pilihan.
        """
        # Jika targetnya hanya satu objek (misalnya, Boss), langsung kembalikan objek itu
        if isinstance(available_targets, Boss):
            return available_targets
        
        # Jika targetnya adalah list (misalnya, player_team)
        elif isinstance(available_targets, list):
            while True:
                print("\nPilih Target:")
                # Filter hanya target yang hidup
                valid_targets = [t for t in available_targets if t.is_alive]
                if not valid_targets: # Jika tidak ada target yang valid (semua KO)
                    print("Tidak ada target yang hidup.")
                    return None

                for i, target in enumerate(valid_targets):
                    print(f"[{i+1}] {target.name} ({int(target.hp)} HP)")
                print("[0] Kembali")
                
                try:
                    choice = int(input("Pilihan Target: > "))
                    if choice == 0:
                        return None
                    if 1 <= choice <= len(valid_targets):
                        return valid_targets[choice - 1]
                    else:
                        print("Pilihan tidak valid.")
                except ValueError:
                    print("Masukkan angka.")
        return None # Mengembalikan None jika tidak ada target atau pilihan tidak valid

    def end_battle(self):
        self.display_ui()
        if not self.boss.is_alive:
            print("\n====================")
            print("  SELAMAT, ANDA MENANG! ")
            print("====================")
        else:
            print("\n====================")
            print("   ANDA KALAH...   ")
            print("====================")
