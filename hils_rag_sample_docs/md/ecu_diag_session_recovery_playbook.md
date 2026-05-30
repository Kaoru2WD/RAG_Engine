# ECU Diag Session Recovery Playbook

## Purpose

CAN 診断セッション遷移を誤って残したまま通常試験に戻した時の、復旧手順を短くまとめる。

## Trigger Conditions

- Extended session のまま ignition cycle を模擬した
- Security access unlock 後に tester が切断された
- `0x7F 0x78` が連続し、通常通信周期が乱れた

## Recovery Pattern

### Pattern A: Soft unwind

1. Tester present を 2 周期維持する
2. `0x10 0x01` で default session を要求
3. 応答確認後、5 秒待って cyclic traffic を再開

### Pattern B: Forced bench reset

前提:
- soft unwind が失敗
- DTC snapshot 採取済み
- 12V recycle による副作用を受容できる

```text
Reset order:
1) Torque inhibit
2) Session log export
3) IGN off
4) 12V drop 3 s
5) IGN on
```

## Non-obvious Assumptions

- default session へ戻っても application side latch が即解除されるとは限らない
- BMS_SIM 側が stale heartbeat を維持していると、復旧したように見えて再現性が崩れる

## Appendix: service IDs seen in the field

| SID | Meaning | Common misuse |
| --- | --- | --- |
| `0x10` | Diagnostic session control | response positive だけ見て内部状態を見ない |
| `0x27` | Security access | seed/key 成功後のタイムアウト管理を忘れる |
| `0x28` | Communication control | mute 範囲を広げすぎて bench 側も見失う |
