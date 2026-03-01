"""
states/states.py — All FSM StatesGroups.
"""
from aiogram.fsm.state import State, StatesGroup


class AddWordStates(StatesGroup):
    waiting_for_russian  = State()
    waiting_for_english  = State()
    waiting_for_topic    = State()


class DeleteWordStates(StatesGroup):
    choosing_word    = State()
    confirming       = State()


class GameStates(StatesGroup):
    choosing_topic = State()
    playing        = State()
