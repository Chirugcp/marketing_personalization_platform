from __future__ import annotations

import json
import os
from datetime import datetime, timedelta
from random import Random

from src.utils.config import settings


MESSAGES = [
    ('pricing', 'Looking for the best price for premium plan'),
    ('discount', 'Do you have any discount for annual renewal'),
    ('support', 'Need help with onboarding setup and support'),
    ('product', 'Interested in AI personalization features'),
    ('renewal', 'My contract is expiring and I want renewal options'),
    ('upsell', 'Can you suggest advanced campaign automation package'),
]
CAMPAIGNS = ['camp_alpha', 'camp_beta', 'camp_gamma', 'camp_delta']


def main() -> None:
    os.makedirs('data', exist_ok=True)
    rng = Random(42)
    now = datetime.utcnow()
    with open(settings.data_path, 'w', encoding='utf-8') as fh:
        for i in range(1, 51):
            user_id = f'user_{(i % 12) + 1:03d}'
            campaign_id = CAMPAIGNS[i % len(CAMPAIGNS)]
            intent, message = MESSAGES[i % len(MESSAGES)]
            payload = {
                'message_id': f'msg_{i:04d}',
                'user_id': user_id,
                'campaign_id': campaign_id,
                'intent': intent,
                'message': f'{message} #{rng.randint(100,999)}',
                'timestamp': (now - timedelta(minutes=i * 7)).isoformat(),
            }
            fh.write(json.dumps(payload) + '\n')


if __name__ == '__main__':
    main()
