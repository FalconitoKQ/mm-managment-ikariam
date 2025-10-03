import datetime

class Battle_ship_stock:
    def __init__(self, stock_taran_parowy, stock_okret_z_taranem, stock_krazownik, stock_balonowiec):
        self.losses_taran_parowy = 15
        self.losses_okret_z_taranem = 18
        self.losses_krazownik = 4
        self.losses_balonowiec = 2

        self.stock_taran_parowy = stock_taran_parowy
        self.stock_okret_z_taranem = stock_okret_z_taranem
        self.stock_krazownik = stock_krazownik
        self.stock_balonowiec = stock_balonowiec

    def losses_per_round_in_all_round(self):
        self.nirs_taran_parowy = self.stock_taran_parowy // self.losses_taran_parowy
        self.nirs_okret_z_taranem = self.stock_okret_z_taranem // self.losses_okret_z_taranem
        self.nirs_krazownik = self.stock_krazownik // self.losses_krazownik
        self.nirs_balonowiec = self.stock_balonowiec // self.losses_balonowiec

    def time_round(self):
        time_now = datetime.datetime.now()
        self.time_round_for_taran_parowy = time_now + datetime.timedelta(minutes=15 * self.nirs_taran_parowy)
        self.time_round_for_okret_z_taranem = time_now + datetime.timedelta(minutes=15 * self.nirs_okret_z_taranem)
        self.time_round_for_krazownik = time_now + datetime.timedelta(minutes=15 * self.nirs_krazownik)
        self.time_round_for_balonowiec = time_now + datetime.timedelta(minutes=15 * self.nirs_balonowiec)