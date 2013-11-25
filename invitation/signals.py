#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.dispatch import Signal

invite_invited = Signal(providing_args=["invite_key"])
invite_accepted = Signal(providing_args=["registered_user", "invite_key"])
