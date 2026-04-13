# Product Brief: SafeCore

## Что Такое SafeCore

SafeCore — это security/control layer для AI-агентов.

Он стоит между агентом и внешними инструментами или системами, оценивает риск и до выполнения действия принимает одно из решений: разрешить, отправить на approval или заблокировать.

## Проблема

Во многих agent-системах путь от вывода модели до вызова инструмента слишком короткий.

Из-за этого появляются реальные риски:

- небезопасное использование инструментов
- рискованные prod-изменения без достаточного контроля
- слабые approval-границы
- неполный audit trail
- неясно, где именно находится контроль execution risk

## Решение

SafeCore вставляет в этот путь явный слой контроля:

- policy evaluation
- data и tool safety checks
- approval gate для рискованных действий
- dry-run-only execution guard
- audit evidence и integrity verification

## Первый Практический Use Case

Самый понятный практический путь в текущем репозитории — встроенный safe HTTP status connector.

Он разрешает только один узкий формат интеграции:

- только `GET`
- только доверенные локальные хосты
- только health/status/metadata/version-пути
- blocked-safe поведение для всего остального

Это важно, потому что показывает: SafeCore уже можно ставить перед реальной connector boundary сегодня, а не только описывать как абстрактный control core.

## Три Состояния Решения

### `ALLOW`

Низкорисковое действие может пройти через guarded path.

Текущее RC-поведение: выполнение остаётся `DRY_RUN_SIMULATED`.

### `NEEDS_APPROVAL`

Рискованное действие остаётся заблокированным, пока нет явного статуса `APPROVED`.

### `DENY`

Очевидно опасное действие остаётся заблокированным и не разблокируется обычным approval-путём.

## Почему Это Важно

SafeCore нужен именно в той точке, где agent capability встречается с реальным операционным риском.

Его ценность не в том, чтобы дать агенту больше возможностей. Его ценность в том, чтобы сделать выполнение контролируемым, проверяемым и аудируемым до того, как что-то коснётся реальной системы.

## Текущее Состояние

SafeCore нужно оценивать как open-source RC/MVP validated core.

Уже сейчас в репозитории есть:

- рабочий guarded execution path
- первый практический allowlisted read-only HTTP status path
- детерминированное поведение `ALLOW / NEEDS_APPROVAL / DENY`
- audit evidence и integrity checks
- runnable demo path
- оформленный release/public documentation pack

Проект нельзя честно называть production-ready platform.

## Что Уже Входит

- Policy Engine
- Data Guard
- Tool Guard
- Execution Guard
- Approval Layer
- Audit Layer
- foundation для Model Router
- hardening connector boundary
- API skeleton
- prompt pack artifacts
- demo и release/public docs

## Что Сознательно Не Входит Пока

- production auth/authz
- реальные external connector side effects
- database persistence
- cloud deployment stack
- UI portal
- enterprise operating depth за пределами текущего validated core
