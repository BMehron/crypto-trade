mock_matcher_pubkey = "8QUAqtTckM5B8gvcuP7mMswat9SjKUuafJMusEoSn1Gy"

sample_orderbook = {
    'timestamp': 1620634947373,
    'pair': {'amountAsset': 'WAVES',
             'priceAsset': '25FEqEjRkqK6yCkiT7Lz6SAYz7gUFCtxfCChnrVFD5AT'},
    'bids': [
        {'amount': 200000000, 'price': 10000000}
    ],
    'asks': [
        {'amount': 9453856021, 'price': 19000000},
        {'amount': 99477247, 'price': 200000000000},
        {'amount': 100000000, 'price': 1900000000000000}
    ]
}

sample_sell_order_accepted = {
    'success': True,
    'message': {
        'version': 3,
        'id': '2CRyxsvDYJ4FVwV5TE3Kqxw7Cr8cmfnhDafVsKY1hEBz',
        'sender': '3MuMdBrKdyDvqkHwbVTwyxhCQ9qEQh8hLmN',
        'senderPublicKey': 'DuasNP39N7PCNCKfEkjXniR8otVbriYp3MpBrKKZrH1K',
        'matcherPublicKey': '8QUAqtTckM5B8gvcuP7mMswat9SjKUuafJMusEoSn1Gy',
        'assetPair': {
            'amountAsset': 'WAVES',
            'priceAsset': '25FEqEjRkqK6yCkiT7Lz6SAYz7gUFCtxfCChnrVFD5AT'
        },
        'orderType': 'sell',
        'amount': 100000,
        'price': 1000000000000000,
        'timestamp': 1620646124605,
        'expiration': 1623238124605,
        'matcherFee': 300000,
        'matcherFeeAssetId': None,
        'signature': '2mSaGAb1f6qmnzjebdm5VfQLU5CoX1Q8u9wEoxVgMeCFhRiQcihrQiYMHiXxkm1guPVGX7EZwoVGLfHLCpYjMVjs',
        'proofs': [
            '2mSaGAb1f6qmnzjebdm5VfQLU5CoX1Q8u9wEoxVgMeCFhRiQcihrQiYMHiXxkm1guPVGX7EZwoVGLfHLCpYjMVjs'
        ]
    },
    'status': 'OrderAccepted'}

sample_order_rejected = {
    "error": 9437184,
    "message": "The order is invalid: amount should be > 0",
    "template": "The order is invalid: {{details}}",
    "params": {
        "details": "amount should be > 0"
    },
    "status": "OrderRejected",
    "success": False
}

sample_order_canceled = {
    'orderId': '2CRyxsvDYJ4FVwV5TE3Kqxw7Cr8cmfnhDafVsKY1hEBz',
    'success': True,
    'status': 'OrderCanceled'
}
