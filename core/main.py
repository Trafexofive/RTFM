#!/usr/bin/env python3
"""
Binary Options Risk Management TUI
Vim-style keybindings for session-based trading
"""

import curses
import argparse
import yaml
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class TradeResult(Enum):
    WIN = "WIN"
    LOSS = "LOSS"
    PUSH = "PUSH"


@dataclass
class Trade:
    timestamp: str
    trade_type: str  # CALL/PUT (optional, for display)
    risk_amount: float
    result: TradeResult
    payout: float
    balance_after: float
    
    def profit_loss(self) -> float:
        if self.result == TradeResult.WIN:
            return self.payout
        elif self.result == TradeResult.LOSS:
            return -self.risk_amount
        return 0.0


class Session:
    def __init__(self, config: Dict):
        self.initial_balance = config['initial_balance']
        self.risk_percent = config['risk_percent']
        self.payout_percent = config['payout_percent']
        self.stop_loss_percent = config.get('stop_loss_percent', 20)
        self.max_consecutive_losses = config.get('max_consecutive_losses', 5)
        
        self.current_balance = self.initial_balance
        self.trades: List[Trade] = []
        self.start_time = datetime.now()
        self.consecutive_wins = 0
        self.consecutive_losses = 0
        self.max_balance = self.initial_balance
        self.min_balance = self.initial_balance
        
    def current_risk_amount(self) -> float:
        return self.current_balance * (self.risk_percent / 100.0)
    
    def add_trade(self, result: TradeResult, trade_type: str = "CALL", custom_risk: Optional[float] = None):
        risk = custom_risk if custom_risk else self.current_risk_amount()
        
        if result == TradeResult.WIN:
            payout = risk * (self.payout_percent / 100.0)
            self.current_balance += payout
            self.consecutive_wins += 1
            self.consecutive_losses = 0
        elif result == TradeResult.LOSS:
            payout = 0.0
            self.current_balance -= risk
            self.consecutive_losses += 1
            self.consecutive_wins = 0
        else:  # PUSH
            payout = 0.0
            
        trade = Trade(
            timestamp=datetime.now().strftime("%H:%M:%S"),
            trade_type=trade_type,
            risk_amount=risk,
            result=result,
            payout=payout,
            balance_after=self.current_balance
        )
        
        self.trades.append(trade)
        self.max_balance = max(self.max_balance, self.current_balance)
        self.min_balance = min(self.min_balance, self.current_balance)
        
        return trade
    
    def undo_last_trade(self) -> bool:
        if not self.trades:
            return False
        
        last_trade = self.trades.pop()
        # Restore balance
        if len(self.trades) > 0:
            self.current_balance = self.trades[-1].balance_after
        else:
            self.current_balance = self.initial_balance
            
        # Recalculate streaks
        self._recalculate_streaks()
        return True
    
    def _recalculate_streaks(self):
        self.consecutive_wins = 0
        self.consecutive_losses = 0
        
        for trade in reversed(self.trades):
            if trade.result == TradeResult.WIN:
                if self.consecutive_losses > 0:
                    break
                self.consecutive_wins += 1
            elif trade.result == TradeResult.LOSS:
                if self.consecutive_wins > 0:
                    break
                self.consecutive_losses += 1
            else:
                break
    
    def should_stop(self) -> tuple[bool, str]:
        # Check stop loss
        drawdown_percent = ((self.initial_balance - self.current_balance) / self.initial_balance) * 100
        if drawdown_percent >= self.stop_loss_percent:
            return True, f"Stop-loss triggered: -{drawdown_percent:.1f}%"
        
        # Check consecutive losses
        if self.consecutive_losses >= self.max_consecutive_losses:
            return True, f"Max consecutive losses: {self.consecutive_losses}"
        
        return False, ""
    
    def stats(self) -> Dict:
        if not self.trades:
            return {
                'total_trades': 0,
                'wins': 0,
                'losses': 0,
                'pushes': 0,
                'win_rate': 0.0,
                'total_pl': 0.0,
                'roi_percent': 0.0,
                'expectancy': 0.0,
                'avg_win': 0.0,
                'avg_loss': 0.0,
                'max_drawdown_percent': 0.0,
                'current_streak': 0,
                'breakeven_wr': 0.0
            }
        
        wins = [t for t in self.trades if t.result == TradeResult.WIN]
        losses = [t for t in self.trades if t.result == TradeResult.LOSS]
        pushes = [t for t in self.trades if t.result == TradeResult.PUSH]
        
        total_trades = len(self.trades)
        win_count = len(wins)
        loss_count = len(losses)
        
        win_rate = (win_count / total_trades * 100) if total_trades > 0 else 0.0
        total_pl = self.current_balance - self.initial_balance
        roi_percent = (total_pl / self.initial_balance) * 100
        
        avg_win = sum(t.payout for t in wins) / len(wins) if wins else 0.0
        avg_loss = sum(t.risk_amount for t in losses) / len(losses) if losses else 0.0
        
        expectancy = (win_rate / 100 * avg_win) - ((100 - win_rate) / 100 * avg_loss)
        
        max_dd = ((self.initial_balance - self.min_balance) / self.initial_balance) * 100
        
        # Breakeven win rate calculation: WR = Risk / (Risk + Payout)
        breakeven_wr = 100 / (1 + self.payout_percent / 100)
        
        current_streak = self.consecutive_wins if self.consecutive_wins > 0 else -self.consecutive_losses
        
        return {
            'total_trades': total_trades,
            'wins': win_count,
            'losses': loss_count,
            'pushes': len(pushes),
            'win_rate': win_rate,
            'total_pl': total_pl,
            'roi_percent': roi_percent,
            'expectancy': expectancy,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'max_drawdown_percent': max_dd,
            'current_streak': current_streak,
            'breakeven_wr': breakeven_wr
        }


class BinOptTUI:
    def __init__(self, stdscr, config: Dict):
        self.stdscr = stdscr
        self.session = Session(config)
        self.scroll_offset = 0
        self.status_message = "Session Active"
        self.command_buffer = ""
        self.mode = "NORMAL"
        
        curses.curs_set(0)
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        
    def draw_box(self, y, x, height, width, title=""):
        try:
            self.stdscr.addstr(y, x, "┌─" + title + "─" * (width - len(title) - 3) + "┐")
            for i in range(1, height - 1):
                self.stdscr.addstr(y + i, x, "│" + " " * (width - 2) + "│")
            self.stdscr.addstr(y + height - 1, x, "└" + "─" * (width - 2) + "┘")
        except curses.error:
            pass
    
    def draw_session_info(self):
        max_y, max_x = self.stdscr.getmaxyx()
        self.draw_box(0, 0, 4, max_x, " SESSION ")
        
        stats = self.session.stats()
        balance_change = self.session.current_balance - self.session.initial_balance
        balance_change_pct = (balance_change / self.session.initial_balance) * 100
        
        balance_color = curses.color_pair(1) if balance_change >= 0 else curses.color_pair(2)
        
        line1 = f"Balance: ${self.session.initial_balance:.2f} → ${self.session.current_balance:.2f} "
        line1 += f"({balance_change_pct:+.1f}%)    Risk/Trade: ${self.session.current_risk_amount():.2f}"
        
        elapsed = datetime.now() - self.session.start_time
        hours = elapsed.seconds // 3600
        minutes = (elapsed.seconds % 3600) // 60
        
        line2 = f"Trades: {stats['total_trades']} | W/L: {stats['wins']}/{stats['losses']} "
        line2 += f"({stats['win_rate']:.1f}%)           Session Time: {hours}h {minutes}m"
        
        try:
            self.stdscr.addstr(1, 2, line1)
            self.stdscr.addstr(2, 2, line2)
        except curses.error:
            pass
    
    def draw_trade_entry(self):
        max_y, max_x = self.stdscr.getmaxyx()
        self.draw_box(4, 0, 5, max_x, f" TRADE ENTRY [{self.mode}] ")
        
        try:
            self.stdscr.addstr(5, 2, "[w] Win    [l] Loss    [p] Push")
            self.stdscr.addstr(6, 2, "Quick: [1-9] for custom % override")
        except curses.error:
            pass
    
    def draw_history(self):
        max_y, max_x = self.stdscr.getmaxyx()
        history_height = max_y - 17
        self.draw_box(9, 0, history_height, max_x, " HISTORY ")
        
        header = "  # │ Time     │ Type │ Risk    │ Result  │ Balance    │ Streak"
        separator = "────┼──────────┼──────┼─────────┼─────────┼────────────┼──────────"
        
        try:
            self.stdscr.addstr(10, 2, header)
            self.stdscr.addstr(11, 2, separator[:max_x-4])
            
            visible_trades = self.session.trades[-self.scroll_offset-history_height+3:]
            visible_trades.reverse()
            
            for i, trade in enumerate(visible_trades[:history_height-3]):
                idx = len(self.session.trades) - i - self.scroll_offset
                
                result_color = curses.color_pair(1) if trade.result == TradeResult.WIN else \
                               curses.color_pair(2) if trade.result == TradeResult.LOSS else \
                               curses.color_pair(3)
                
                pl = trade.profit_loss()
                streak_str = f"W{self.session.consecutive_wins}" if pl > 0 else \
                            f"L{self.session.consecutive_losses}" if pl < 0 else ""
                
                line = f"{idx:3d} │ {trade.timestamp} │ {trade.trade_type:4s} │ ${trade.risk_amount:7.2f} │ "
                line += f"{pl:+8.2f} │ ${trade.balance_after:9.2f} │ {streak_str:8s}"
                
                self.stdscr.addstr(12 + i, 2, line[:max_x-4], result_color)
        except curses.error:
            pass
    
    def draw_stats(self):
        max_y, max_x = self.stdscr.getmaxyx()
        stats_y = max_y - 7
        self.draw_box(stats_y, 0, 5, max_x, " STATS ")
        
        stats = self.session.stats()
        
        line1 = f"Expectancy: ${stats['expectancy']:+.2f}/trade    "
        line1 += f"ROI: {stats['roi_percent']:+.1f}%    "
        line1 += f"Max DD: {stats['max_drawdown_percent']:.1f}%"
        
        line2 = f"Avg Win: ${stats['avg_win']:+.2f}           "
        line2 += f"Avg Loss: ${stats['avg_loss']:+.2f}"
        
        streak_indicator = "✓" if stats['win_rate'] >= stats['breakeven_wr'] else "✗"
        line3 = f"Est. Breakeven WR: {stats['breakeven_wr']:.1f}%   "
        line3 += f"Actual: {stats['win_rate']:.1f}% {streak_indicator}"
        
        try:
            self.stdscr.addstr(stats_y + 1, 2, line1)
            self.stdscr.addstr(stats_y + 2, 2, line2)
            self.stdscr.addstr(stats_y + 3, 2, line3)
        except curses.error:
            pass
    
    def draw_status_bar(self):
        max_y, max_x = self.stdscr.getmaxyx()
        stop_loss_amount = self.session.initial_balance * (1 - self.session.stop_loss_percent / 100)
        
        status = f"[{self.mode}] :help for commands | {self.status_message} | Stop-Loss: ${stop_loss_amount:.2f}"
        
        if self.mode == "COMMAND":
            status = ":" + self.command_buffer
        
        try:
            self.stdscr.addstr(max_y - 1, 0, status[:max_x-1], curses.color_pair(4))
        except curses.error:
            pass
    
    def handle_command(self, cmd: str):
        parts = cmd.strip().split()
        if not parts:
            return
        
        command = parts[0]
        
        if command in ['q', 'quit']:
            return "QUIT"
        elif command == 'w':
            self.status_message = "Session saved (not implemented yet)"
        elif command == 'wq':
            return "QUIT"
        elif command == 'reset':
            self.session = Session({'initial_balance': self.session.initial_balance,
                                   'risk_percent': self.session.risk_percent,
                                   'payout_percent': self.session.payout_percent})
            self.status_message = "Session reset"
        elif command == 'risk' and len(parts) > 1:
            try:
                self.session.risk_percent = float(parts[1])
                self.status_message = f"Risk set to {self.session.risk_percent}%"
            except ValueError:
                self.status_message = "Invalid risk value"
        elif command == 'payout' and len(parts) > 1:
            try:
                self.session.payout_percent = float(parts[1])
                self.status_message = f"Payout set to {self.session.payout_percent}%"
            except ValueError:
                self.status_message = "Invalid payout value"
        elif command == 'help':
            self.status_message = "w=win l=loss p=push dd=undo :q=quit :risk N :payout N"
        else:
            self.status_message = f"Unknown command: {command}"
    
    def run(self):
        while True:
            self.stdscr.clear()
            
            self.draw_session_info()
            self.draw_trade_entry()
            self.draw_history()
            self.draw_stats()
            self.draw_status_bar()
            
            self.stdscr.refresh()
            
            # Check stop conditions
            should_stop, reason = self.session.should_stop()
            if should_stop:
                self.status_message = f"SESSION STOPPED: {reason}"
                self.stdscr.refresh()
                curses.napms(3000)
                break
            
            try:
                key = self.stdscr.getch()
            except KeyboardInterrupt:
                break
            
            if self.mode == "COMMAND":
                if key == 27:  # ESC
                    self.mode = "NORMAL"
                    self.command_buffer = ""
                elif key == 10:  # ENTER
                    result = self.handle_command(self.command_buffer)
                    self.command_buffer = ""
                    self.mode = "NORMAL"
                    if result == "QUIT":
                        break
                elif key == 127 or key == curses.KEY_BACKSPACE:  # BACKSPACE
                    self.command_buffer = self.command_buffer[:-1]
                elif 32 <= key <= 126:  # Printable characters
                    self.command_buffer += chr(key)
            else:  # NORMAL mode
                if key == ord('w'):
                    self.session.add_trade(TradeResult.WIN)
                    self.status_message = "WIN logged"
                elif key == ord('l'):
                    self.session.add_trade(TradeResult.LOSS)
                    self.status_message = "LOSS logged"
                elif key == ord('p'):
                    self.session.add_trade(TradeResult.PUSH)
                    self.status_message = "PUSH logged"
                elif key == ord('u'):
                    if self.session.undo_last_trade():
                        self.status_message = "Last trade undone"
                    else:
                        self.status_message = "No trades to undo"
                elif key == ord('j'):
                    self.scroll_offset = max(0, self.scroll_offset - 1)
                elif key == ord('k'):
                    self.scroll_offset = min(len(self.session.trades) - 1, self.scroll_offset + 1)
                elif key == ord('g'):
                    self.scroll_offset = 0
                elif key == ord('G'):
                    self.scroll_offset = len(self.session.trades) - 1
                elif key == ord(':'):
                    self.mode = "COMMAND"
                    self.command_buffer = ""
                elif key == ord('q'):
                    break


def load_config(config_path: str) -> Dict:
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        # Default config
        return {
            'initial_balance': 2000.0,
            'risk_percent': 5.0,
            'payout_percent': 80.0,
            'stop_loss_percent': 20.0,
            'max_consecutive_losses': 5
        }


def main():
    parser = argparse.ArgumentParser(description='Binary Options Risk Management TUI')
    parser.add_argument('-c', '--config', default='config.yml', help='Path to config file')
    args = parser.parse_args()
    
    config = load_config(args.config)
    
    curses.wrapper(lambda stdscr: BinOptTUI(stdscr, config).run())


if __name__ == '__main__':
    main()
