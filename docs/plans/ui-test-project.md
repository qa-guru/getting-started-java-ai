# План развития учебного проекта UI-автотестов

## Назначение

Постепенно добавить TestBase, независимые сценарии, Page Object, Allure-отчёты (по решению фазы 4 — генератор Allure Report 2), GitHub Actions, Telegram и Jenkins, сохраняя существующий Java-стек.

В этом документе хранятся согласованные решения, статусы фаз, результаты проверок, ограничения и открытые вопросы. Общие правила работы агента находятся отдельно в [AGENTS.md](../../AGENTS.md). После каждой фазы обновлять этот план; не отмечать выполнение без подтверждённых результатов.

## Согласованные решения

- Java 21 через Gradle Java toolchain; Gradle Wrapper 9.6.0, bin-дистрибутив.
- Selenide 7.19.0 (Selenium 4.51.0, CDP v153–v155), JUnit Jupiter 6.1.3; версия поднята в фазе 9 (findings фазы 8). Версии зависимостей без согласования не менять.
- Defaults: baseUrl=https://github.com, browser=chrome, browserSize=1920x1080, headless=false.
- Переопределение через -DbaseUrl, -Dbrowser, -DbrowserSize, -Dheadless с явной передачей этих свойств из Gradle в JVM тестов. Дополнительно (фаза 5) Gradle передаёт `selenide.browserBinary`, `webdriver.chrome.driver` и `chromeoptions.args` только если они заданы; без них локальное поведение не меняется.
- В CI явно передавать headless=true.
- Page Object: fluent API; проверки в should…-методах страниц; private final SelenideElement-поля; имена методов описывают пользовательские действия.
- Отдельные компоненты выделять только при реальном повторении блоков. Не добавлять BasePage, фабрики и сложную конфигурационную систему без необходимости.
- Структура Page Object: packages `tests` (SearchTests, TestBase) и `pages` (SearchPage, SearchResultsPage). open("/search") живёт в SearchPage.open() и остаётся относительным к baseUrl; assertions — в should…-методах страниц (shouldHaveResult, shouldBeEmpty) с исходными локаторами и порядком проверок.
- Отчёты: генератор — Allure Report 2 CLI 2.46.1 (локально через Homebrew; в CI — официальный tgz с Maven Central с закреплённым SHA-256); Node.js и npm-зависимости в проект не вводятся (решение пользователя на этапе A фазы 4 вместо изначального Report 3).
- JVM-адаптеры: Allure Java 3.0.0 — `allure-jupiter` (JUnit 5 и 6) + `allure-selenide` (Selenide 7.x), версии выравниваются через `allure-bom`; формат результатов совместим с генератором Report 2.
- Шаги в отчёте: `@Step` на методах страниц (требует `-javaagent:aspectjweaver` на JVM тестов, версия 1.9.25) + технические шаги Selenide от `AllureSelenide` (вкладываются в пользовательские). Вложения — Screenshot и Page source только при падении (дефолты `AllureSelenide`); listener регистрируется в `@BeforeAll` TestBase — это выполняется на каждый тестовый класс, а не один раз на JVM; повторный вызов `addListener("allure", …)` заменяет listener с тем же именем.
- Результаты Allure — `build/allure-results` (`src/test/resources/allure.properties`), отчёт — `build/allure-report`; оба каталога внутри `build/` и не попадают в git.

## Текущее состояние

Последняя сверка файлов и git: 2026-10-19 (фаза 9).

- Фаза 0 завершена; исходный запуск проверен в этой переписке.
- Фаза 1 завершена по отчёту пользователя. Коммит e55ae45ae599cdfa83cfac608dbe96b42d0a3916 и соответствующая конфигурация подтверждены чтением репозитория; браузерные проверки фазы 1 при сохранении плана не повторялись.
- Реализация и проверки тестов фазы 2 подтверждены исходниками, коммитом 3cefd221898c108ba538f5daee1ea4c30e76d615 и предоставленным отчётом фазы 3: все три теста выполнены отдельно, с defaults и в headless. Сведения о первоначальном согласовании сценариев и риск данных второго негативного сценария остаются открытыми.
- Фаза 3 завершена по отчёту пользователя, коммит 1312c8da32be42e5351af1334cf0bf035c65ab54 подтверждён в истории: локаторы и взаимодействия перенесены в pages.SearchPage и pages.SearchResultsPage, тесты и TestBase перемещены в package tests. Структура и сохранение assertions подтверждены чтением файлов; браузерные проверки при обновлении плана не повторялись.
- Фаза 4 завершена в этой сессии: Allure Java 3.0.0 (адаптеры) + Allure Report 2.46.1 CLI (генератор); проверки и ограничения — в разделе фазы 4.
- Фаза 5 завершена по отчёту: workflow проверен локально и в реальном GitHub Actions — успешные, контролируемые и диагностические запуски перечислены в разделе фазы 5. Успешный запуск 38311448403 повторно подтверждён через API в фазе 8.
- Фазы 6 и 7 отложены по решению пользователя в домашнее задание учащимся; в демонстрационном проекте не реализуются. Фаза 6 выполнена учащимся 2026-10-18 (этапы A–D: согласование, реализация, проверка на fixtures, реальная отправка) — статус, решения и проверки зафиксированы в разделе фазы 6; фаза 7 (Jenkins) не начата.
- Фаза 8 (Review) выполнена 2026-10-17: объём фаз 0–5 проверен без изменения кода, workflow и инфраструктуры; findings, проверки и ограничения — в разделе фазы 8.
- Фаза 9 (доработка findings фазы 8) выполнена 2026-10-19: установлена причина sandbox-падения Chrome, обновлены Selenide и CfT, Pages публикуется только при зелёных тестах, усилены Actions permissions, добавлена очистка allure-results — детали и проверки в разделе фазы 9.

Порядок дальнейшей работы: демонстрационный объём фаз 0–5 завершён и проверен; фазы 6–7 выполняются учащимися отдельно, сначала согласование, затем по одной фазе с проверкой и собственным коммитом. Задание для учащихся (два варианта: полный путь 0–8 и короткий путь 6–7): [docs/homework.md](../homework.md).

## Фаза 0 — Baseline

Статус: завершена с зафиксированными ограничениями.

- [x] Изучить сборку, тесты и настройки, проверить git.
- [x] Проверить wrapper: исходно отсутствовал.
- [x] Определить фактические версии и требования Java: Selenide и JUnit требуют Java 17+, локально использовалась Java 21.
- [x] Запустить исходный тест без изменения кода: BUILD SUCCESSFUL, задача test выполнена с --rerun-tasks.
- [x] Согласовать параметры, Java, wrapper и стиль Page Object.

Проверенная команда из корня репозитория:

```bash
gradle test --tests SearchTests.successfulSearchTest --rerun-tasks --console=plain
```

Ограничения: один успешный запуск не доказывает стабильность внешнего GitHub; запрос qa.guru зависит от изменяемых данных. Чтение JUnit XML в build/ блокировалось правилами IDE, даже после запроса доступа.

## Фаза 1 — TestBase

Статус: завершена по отчёту пользователя.

Коммит: e55ae45ae599cdfa83cfac608dbe96b42d0a3916 — Make UI tests reproducible and isolate browser sessions.

- [x] Добавить штатный Gradle Wrapper 9.6.0 с официальным checksum и executable bit для gradlew.
- [x] Зафиксировать Java 21 toolchain.
- [x] Добавить TestBase: настройка Selenide в @BeforeEach, closeWebDriver в @AfterEach.
- [x] Передавать только четыре согласованных свойства в JVM тестов.
- [x] Подключить TestBase к SearchTests и заменить абсолютный URL на /search.
- [x] Проверить defaults, переопределение свойств и использование baseUrl внутри JVM тестов.
- [x] Проверить отсутствие запуска браузера при настройке, изоляцию сессий и cleanup после успеха и контролируемого падения.
- [x] Удалить временную диагностику, восстановить исходный assertion, повторить успешные запуски и создать отдельный коммит без push.

По отчёту оба финальных запуска завершились BUILD SUCCESSFUL:

```bash
./gradlew test --tests SearchTests.successfulSearchTest --rerun-tasks --console=plain
./gradlew test --tests SearchTests.successfulSearchTest -DbaseUrl=https://www.github.com -Dbrowser=chrome -DbrowserSize=1366x768 -Dheadless=true --rerun-tasks --console=plain
```

Ограничения: macOS ограничила высоту видимого окна до 1050 при настройке 1920x1080; Selenium предупреждал о CDP Chrome 155 и поддерживаемой версии 153. Windows, другие браузеры и CI не проверялись. XML не читался; диагностика получена из stdout.

## Фаза 2 — Tests

Статус: реализация и выполнение тестов подтверждены; первоначальное согласование сценариев и оценка устойчивости данных остаются открытыми.

Коммит: 3cefd221898c108ba538f5daee1ea4c30e76d615 — Add negative GitHub search tests for deterministic empty results.

Источник результатов запуска — предоставленный пользователем отчёт фазы 3. При обновлении плана тесты не перезапускались. Отсутствие сведений о согласовании в этой сессии не означает, что согласование не проводилось.

### Этап A — исследование и согласование, без изменения кода

- [ ] Зафиксировать первоначальное подтверждение пользователем двух дополнительных сценариев.
- [x] Проверить доступность сценариев в реальном UI: по отчёту фазы 3 все три теста выполнены и прошли после восстановления доступности GitHub.
- [ ] Зафиксировать обоснование целей, предусловий, данных, assertions, локаторов и рисков обоих дополнительных сценариев.
- [ ] Подтвердить отсутствие зависимости от неконтролируемых данных для второго негативного сценария.

В реализованных тестах используются noResultsForImpossibleStarsRangeTest (stars:<0) и noResultsForHugeStarsCountTest (stars:>999999999). Проверяются тексты empty state и отсутствие results-list, а не случайный порядок выдачи. Огромный порог stars сам по себе не доказывает логическую невозможность совпадений; этот риск сохраняется. Поисковые данные и assertions не изменять в рамках обновления плана или подключения Allure.

### Этап B — реализация и проверка

- [x] Добавить два независимых теста в SearchTests; сведения о первоначальном согласовании отмечены отдельно выше.
- [x] Сохранить исходный сценарий: qa.guru и проверку текста QA.GURU.
- [x] Использовать TestBase, относительный /search, ожидания Selenide и содержательные assertions.
- [x] Проверить каждый новый тест отдельно, весь набор с defaults и в headless — по отчёту фазы 3.
- [x] Установить причину наблюдённого падения: GitHub HTTP 429, по отчёту фазы 3; после снятия ограничения набор прошёл без изменения кода.
- [x] Удалить временную диагностику и создать отдельный коммит реализации; в текущих tracked Java-файлах временной диагностики нет.

Итог по отчёту фазы 3: tests=3, failures=0, skipped=0 в успешном полном запуске. HTTP 429 и зависимость от внешних данных остаются ограничениями, а не устранёнными дефектами.

## Фаза 3 — Page Object

Статус: завершена по предоставленному пользователем отчёту.

Коммит: 1312c8da32be42e5351af1334cf0bf035c65ab54 — Extract GitHub search page objects from tests.

- [x] Подтвердить применимость согласованного стиля к фактическим сценариям.
- [x] Перенести взаимодействия и локаторы в страницы, проверки — в should…-методы.
- [x] Проверить необходимость компонентов: повторяющихся блоков нет, компоненты и BasePage не добавлены.
- [x] Сохранить сценарии и поведение; проверить весь набор и закоммитить изменения.

Итоговая структура: `tests.SearchTests`, `tests.TestBase`, `pages.SearchPage` (open + searchFor), `pages.SearchResultsPage` (shouldHaveResult, shouldBeEmpty). Локаторы, тестовые данные, assertions и порядок проверок сохранены без изменений; это подтверждено сравнением исходников с коммитом фазы 2. Полный переход на пакеты tests и pages подтверждён пользователем в отчёте этапа A.

По отчёту фазы 3 выполнены следующие проверки:

- Каждый тест отдельно: `./gradlew test --tests "tests.SearchTests.<method>"` для трёх методов — BUILD SUCCESSFUL, tests=1, failures=0 в каждом запуске.
- Полный набор: `./gradlew test --rerun-tasks --console=plain` — BUILD SUCCESSFUL, 3/3.
- Headless: `./gradlew test -Dheadless=true -DbrowserSize=1366x768 --rerun-tasks --console=plain` — первый запуск упал на третьем тесте с GitHub HTTP 429; после восстановления доступности повторный полный запуск прошёл, tests=3, failures=0, skipped=0.
- Причина 429 установлена по странице ошибки и подтверждена curl с того же IP; успешный запуск после снятия лимита выполнен без изменения кода. Это не автоматический ретрай и не устранение внешнего ограничения.
- В отчёте фазы 3 проверка git diff --check прошла, временная диагностика отсутствовала, после коммита дерево было чистым.

При этом обновлении плана подтверждены история и исходники, но UI-тесты, JUnit XML и сетевые ответы повторно не проверялись. Ранее обнаруженные незакоммиченные whitespace-изменения page-классов убраны 2026-10-15 (были только trailing whitespace, без семантики); дерево чистое.

Ограничения: внешний GitHub может отвечать HTTP 429 при частых запросах; точный порог и длительность ограничения не установлены. Windows, другие браузеры и реальный CI не проверялись. Предупреждение CDP сохраняется.

## Фаза 4 — Allure Report 3

Статус: завершена с изменением решения — генератор Allure Report 2 вместо Report 3.

На этапе A пользователь отклонил Node.js-зависимость генератора Report 3 (npm `allure` 3.x) и выбрал Report 2 через Homebrew. Название фазы оставлено как в исходном плане; фактический генератор — Allure Report 2 CLI 2.46.1. JVM-адаптеры — Allure Java 3.0.0.

- [x] Разделить JVM-адаптеры Allure и CLI-генератор отчёта: адаптеры пишут `build/allure-results`, brew `allure` собирает HTML в `build/allure-report`.
- [x] Проверить совместимость с фактическими Java 21, JUnit 6 и Selenide: allure-java 3.0.0 требует Java 17+ и заявляет работу с JUnit 6 и 5; allure-selenide нацелен на Selenide 7.x; формат результатов Allure Java 3 читается Report 2 (официальный migration guide). Понижать Java, JUnit или Selenide не потребовалось.
- [x] Выбрать и зафиксировать проверенные версии: allure-bom/allure-jupiter/allure-selenide 3.0.0 (релиз 2026-09-11), aspectjweaver 1.9.25 (2025-11-04), CLI `allure` 2.46.1 (обновлён с 2.36.0 через brew по запросу пользователя).
- [x] Проверить актуальную документацию и встроенный --help: `allure --version` → 2.46.1; команды `generate` (`-o/--report-dir`, `--clean`, `--single-file`), `open` (`-h`, `-p`), `serve`; отдельного `--help` у субкоманд в 2.x нет.
- [x] Согласовать шаги и вложения: `@Step` на методах страниц + технические шаги Selenide (выбор пользователя), Screenshot + Page source при падении (дефолты AllureSelenide).
- [x] Сгенерировать и открыть отчёт, проверить диагностику контролируемого падения.
- [x] Восстановить успешное состояние, исключить generated artifacts из git и создать коммит.

Проверки этой сессии (2026-10-12):

- `./gradlew test --rerun-tasks --console=plain` — BUILD SUCCESSFUL, 3/3 passed; создано 3 `*-result.json` + контейнеры в `build/allure-results`.
- Дерево шагов в результатах: пользовательские `@Step` с подстановкой параметров («Search for "qa.guru"») и вложенные технические шаги Selenide (`$("open")`, `set value`, `should have`, `webdriver create/close`).
- `allure generate build/allure-results --clean -o build/allure-report`; `allure open build/allure-report -h 127.0.0.1 -p 45624` — сервер отвечает HTTP 200; в данных отчёта (`suites.json`, `test-cases/*.json`) все 3 теста passed с полным деревом шагов. UI показан пользователю через browser preview.
- Контролируемое падение: в `successfulSearchTest` ожидаемый текст временно заменён на `QA.GURU-NO-SUCH-TEXT`. Gradle вернул exit code 1 (BUILD FAILED); причина — намеренный assertion `Element should have text "QA.GURU-NO-SUCH-TEXT"`, не HTTP 429. На упавшем шаге записаны Screenshot (PNG) и Page source (HTML), файлы вложений существуют на диске; stack trace присутствует. После падения браузерных процессов не осталось; `webdriver close()` записан как passed.
- Изоляция прогонов: `build/allure-results` очищался перед прогоном падения и перед финальным прогоном; отчёт падения собран отдельно в `build/allure-report-failure`.
- Финальное состояние: assertion восстановлен, `./gradlew test --rerun-tasks` — 3/3 passed, exit code 0; отчёт пересобран в `build/allure-report`.

Ограничения: версия CLI не фиксируется в репозитории (brew-установка глобальна; на момент проверки — 2.46.1), lock-файла нет — осознанный компромисс отказа от Node.js. Отчёт был открыт пользователю через browser preview, но явной визуальной приёмки от пользователя не зафиксировано (исправлено при фазе 5); данные отчёта проверены программно (HTTP 200 и JSON), что визуальную приёмку не заменяет. Windows/Linux и реальный CI не проверялись; внешний GitHub может отвечать HTTP 429.

## Фаза 5 — GitHub Actions

Статус: завершена — workflow проверен локально и в реальном GitHub Actions (см. ниже).

Файлы: [.github/workflows/ui-tests.yml](../../.github/workflows/ui-tests.yml), `build.gradle` (необязательная передача `selenide.browserBinary` и `webdriver.chrome.driver`). Коммит реализации: d473a0242d2952534fe9106f1398ebebe76522d3.

### Согласовано на этапе A (2026-10-12)

- [x] События: только `workflow_dispatch`; push, pull_request и расписание не используются.
- [x] Публикация: артефакты (retention 14 дней) и публичный GitHub Pages (source = GitHub Actions). Pages публикуется только для запусков из default branch при успешно сгенерированном отчёте; с фазы 9 — и только при зелёных тестах (решение publish-always пересмотрено, см. фазу 9).
- [x] Inputs: `browser` (choice, только `chrome`) и `browserSize` (`^[0-9]{3,4}x[0-9]{3,4}$`). baseUrl зафиксирован как https://github.com, выбор тестов не предусмотрен, headless=true всегда.
- [x] Браузер: Chrome for Testing + ChromeDriver одной версии; исходно 153.0.8010.52 (поддержка CDP в Selenium 4.49.0 — v151–153), в фазе 9 обновлено до 155.0.8059.84 (Stable на 2026-10-19, Selenium 4.51.0 — CDP v153–v155); пути передаются в тесты через Gradle-свойства.
- [x] Репозиторий для реального CI: отдельный публичный `qa-guru/getting-started-java-ai` (remote `ai`); `origin` (qa-guru/getting-started-java) не меняется.
- [x] GitHub secrets в фазе 5 не используются. Имена secrets/credentials, Telegram-уведомления (из каких CI, для каких исходов), расположение Jenkins и агента (ОС, label, инструменты) пока неизвестны — открытые вопросы фаз 6–7.

### Решения workflow

- Runner `ubuntu-24.04` (не `-latest`), `timeout-minutes: 30`.
- Actions закреплены по SHA (версии опубликованы не позже чем за 7 дней до выбора):
  - `actions/checkout` v7.0.1 `3d3c42e5aac5ba805825da76410c181273ba90b1`, `persist-credentials: false`;
  - `actions/setup-java` v6.0.1 `de7274f081f381c8f8158605e0321c36c376e2e6`, Temurin 21;
  - `gradle/actions/setup-gradle` v6.4.0 `3f5f9adaf7d9fecd50b5935e54106014257a94e6`;
  - `browser-actions/setup-chrome` v2.2.0 `48ad923757ca74d66703209fe939badbdf80f2f4`;
  - `actions/upload-artifact` v7.0.1 `043fb46d1a93c77aae656e7c1c64a875d1fc6a0a` (v7.0.2 моложе 7 дней на момент выбора);
  - `actions/upload-pages-artifact` v5.0.0 `fc324d3547104276b827a68afc52ff2a11cc49c9`;
  - `actions/deploy-pages` v5.0.1 `368f82528645a54fb793d4d04e342629a3f51346`.
- Allure CLI: `https://repo.maven.apache.org/maven2/io/qameta/allure/allure-commandline/2.46.1/allure-commandline-2.46.1.tgz`, SHA-256 `37428164f310c8d137cfdd2c3a25d049b233261ddab13e1bd4dfd7627b5cbf8d` — совпадает с digest ассета `allure-2.46.1.tgz` в GitHub Release allure-framework/allure2 и с `.sha1` Maven Central. Генератор использует `JAVA_HOME` из setup-java; workflow проверяет Java 21, совпадение версий Chrome/ChromeDriver и версию Allure.
- Permissions: `contents: read` на уровне workflow; `pages: write` и `id-token: write` только у job `deploy-report`. `pull_request_target` и secrets не используются.
- Concurrency: одна глобальная группа `ui-tests-github-search` без отмены текущего запуска — снижает риск HTTP 429. GitHub держит не больше одного ожидающего запуска в группе, более ранний ожидающий отменяется. Матрицы, параллельных тестов и ретраев нет.
- Inputs передаются только через `env` и процитированные аргументы, после проверки по allowlist/regex.
- Шаги: compile (`./gradlew testClasses`) отдельно от `./gradlew test`. После успешной компиляции, даже при падении тестов, загружаются `allure-results` и `junit-and-gradle-report` (`build/test-results/test`, `build/reports/tests/test`), затем генерируется отчёт. Без `*-result.json` генерация явно падает, пустой отчёт не создаётся. Загрузка сырых результатов идёт до генерации, поэтому ошибка генерации её не блокирует. Без `continue-on-error`, `|| true` и `tee`.
- Каждый запуск идёт на чистом runner; `build/` не кэшируется, чужие артефакты не скачиваются.

Ожидаемое поведение:

| Сценарий | Итог job | Артефакты |
|---|---|---|
| Тесты прошли | success | results, JUnit/Gradle HTML, report; Pages для default branch |
| Падение assertion | failure (exit code Gradle) | то же, с Screenshot и Page source в results |
| Ошибка компиляции | failure на шаге Compile tests | нет |
| Ошибка генерации | failure на шаге Generate | results и JUnit/Gradle HTML |
| Нет результатов | failure на шаге Generate, `::error::No Allure test results` | только то, что создано |

### Локальная проверка (macOS, 2026-10-12)

- `actionlint` 1.7.12 (release-бинарь с проверкой checksum, вне проекта) со встроенным shellcheck — 0 ошибок.
- Передача свойств через Gradle (временный init-скрипт в /tmp, `test --dry-run`): без свойств — только четыре исходных значения; с `-Dselenide.browserBinary="/opt/c t/chrome" -Dwebdriver.chrome.driver=…` оба значения доходят до `Test.systemProperties`, путь с пробелом сохраняется. Selenide 7.18.2 читает `selenide.browserBinary` (`SelenideConfig`), Selenium 4.49.0 — `webdriver.chrome.driver`.
- Скрипт установки CLI: скачивание с Maven Central, `allure --version` → 2.46.1, `JAVA_HOME` = Java 21. `sha256sum --check --strict` локально не проверен: на macOS BSD-утилита без `--strict`, GNU coreutils и Docker недоступны. Сам checksum сверен через `shasum -a 256`.
- Логика «нет результатов» на пустом каталоге выдаёт ошибку; `allure generate` на результатах фазы 4 → summary passed=3, total=3.
- UI-тесты локально не перезапускались (риск 429; Java-код не менялся).
- Linux-окружение локально не проверено: Docker daemon не запущен.

### Проверка в реальном GitHub Actions (2026-10-12)

Репозиторий `qa-guru/getting-started-java-ai` (public, remote `ai`, создан через `gh repo create`; Pages включены через `POST /pages` build_type=workflow). Workflow регистрировался только после push-триггерного probe — особенность GitHub: dispatch-only workflow не индексировался по push на default branch; зарегистрировался после временного `on: [push]` на probe-ветке, затем `workflow_dispatch` заработал, временный триггер не вошёл в master.

Реальные запуски (run id → результат):

- **38308963339** (probe-ветка): dispatch-probe успешен — workflow зарегистрирован.
- **38309018121** (push-probe): ошибка на уровне workflow ещё до выполнения jobs (0 jobs) — не запуск тестов.
- **38309080672** (master): падение — `SessionNotCreatedException`, Chrome instance exited; заодно выявил отказ deploy-report: environment `github-pages` допускал только `main`. Исправлено: branch policy `master` добавлена через API (существующая `main` оставлена). Примечание фазы 8: в этом запуске failed-отчёт был опубликован на Pages — поведение publish-always, согласованное на этапе A, подтверждено фактом.
- **38309549023** (master): падение — то же; шаг setuid-helper искал файл `chrome-sandbox`, которого нет в архиве CfT (фактическое имя — `chrome_sandbox`), поэтому chmod 4755 фактически не применялся (уточнено в фазе 8).
- **38309814119** (master): падение — то же; `chown root:root` + 4755 также не применялся по той же причине.
- **38310176235** (ci-check/diag, временная ветка): диагностика — `chrome --headless --dump-dom` падает без `--no-sandbox` и работает с ним; причина падения в логе обрезана и не установлена (вероятна AppArmor-блокировка user namespaces для CfT на Ubuntu 23.10+ — гипотеза, не подтверждена); `--no-sandbox` при этом не доходил до ChromeOptions (см. следующий запуск).
- **38309984893** (master): падение — `-Dselenide.chromeoptions.args` не сработал: Gradle прокидывает только whitelisted свойства, да и имя у Selenide другое.
- **38310305965** (master): падение — `selenide.chromeoptions.args` неприменим: Selenide 7 читает plain-свойство `chromeoptions.args` (список через запятую), подтверждено по исходникам `ChromeDriverFactory`/`AbstractChromiumDriverFactory`.
- **38310531034** (master): **успех** — BUILD SUCCESSFUL, 3/3 теста; артефакты allure-results (4 КБ), junit-and-gradle-report, allure-report, github-pages; Pages развёрнут: https://qa-guru.github.io/getting-started-java-ai/ отвечает HTTP 200, `widgets/summary.json`: passed=3, total=3.
- **38310722420** (ci-check/assertion-fail): контролируемое падение assertion (`QA.GURU-NO-SUCH-TEXT`) — Run UI tests failure; allure-results с PNG+HTML-вложениями, JUnit XML и report загружены; Pages-шаг и deploy-report пропущены (не default branch). Ветка удалена.
- **38310878425** (ci-check/compile-fail): ошибка компиляции — Compile tests failure; tests, uploads и generate пропущены; артефактов нет. Ветка удалена.
- **38311003194** (ci-check/no-results): `./gradlew noSuchTask` — Run UI tests failure; Generate падает с `::error::No Allure test results`, отчёт с нулём тестов не создан, uploads отчёта пропущены. Ветка удалена.
- **38311448403** ([запуск](https://github.com/qa-guru/getting-started-java-ai/actions/runs/38311448403), master, commit 9799a61): ui-tests и deploy-report — success, BUILD SUCCESSFUL, 3/3 теста; Pages обновлены. Подтверждён повторно в фазе 8 через GitHub API: headSha `9799a61955dbbeacd52fbc59d199f0f17fe6d1bf`, jobs, steps, логи и содержимое артефактов проверены.

В review не считать все красные запуски контролируемыми: в истории есть также реальные ошибки запуска Chrome, передачи свойств и настройки Pages. Последний зелёный запуск не отменяет этой истории и не доказывает отсутствие риска HTTP 429.

Итоговые решения по браузеру (исторически): Chrome падал на этом runner без `--no-sandbox` — аргумент передавался только в CI через `-Dchromeoptions.args=--no-sandbox`; локальные запуски без него. Компромисс был принят: ephemeral runner, открывается только github.com. Уточнение фазы 8: настоящая причина падения не установлена (лог диагностики обрезан); setuid-helper фактически не применялся из-за неверного имени файла — вероятная причина (AppArmor/userns) оставалась неподтверждённой гипотезой. Фаза 9: причина подтверждена, `--no-sandbox` заменён AppArmor-профилем для бинаря CfT — см. фазу 9.

Изменённые файлы фазы: `.github/workflows/ui-tests.yml`, `build.gradle` (проброс `selenide.browserBinary`, `webdriver.chrome.driver`, `chromeoptions.args` — только если заданы), этот план. Коммиты: d473a02 (workflow), 3c490e5 (промежуточный план), 24bea81→f253482 (исправления CI: Pages policy, chrome sandbox helper → удалён, chromeoptions.args), финальный коммит плана — ниже.

Ограничения: один успешный прогон не доказывает стабильность при HTTP 429; входное значение `browserSize` влияет только на окно; macOS/Windows-агенты не используются; push/pull_request-триггеры и секреты отсутствуют; Pages публичны для всего интернета; визуальная приёмка отчёта на Pages пользователем не зафиксирована (проверено: HTTP 200 + summary.json).

## Фаза 6 — Telegram

Статус: выполнена учащимся 2026-10-18 (короткий путь, Вариант B), этапы A–D пройдены. Подробности, решения и результаты проверок — в [phase6-telegram-notes.md](phase6-telegram-notes.md). Коммиты `1ffe2bc`, `cb50947` на ветке `dz-oct-12-6` (переименована из `dz1`), репозиторий `KonstantinKshnyakin/qa-guru-ai-getting-started-java-ai`.

### Перед реализацией согласовать

- [x] Нужны ли уведомления из GitHub Actions и Jenkins и для каких исходов.
- [x] Имена secrets/credentials, поведение при отсутствии секретов и ошибке Telegram.
- [x] Разрешение на реальную отправку сообщения.

### Реализация и проверка

- [x] Использовать secrets окружения без хардкода и логирования.
- [x] Брать passed/failed/skipped из проверенного формата JUnit XML; не опираться на непроверенные внутренние файлы Allure-отчёта.
- [x] Отличать сбой сборки до запуска тестов от успешного запуска с нулём тестов.
- [x] Включить проект, CI, branch/commit, статус тестов, статистику и ссылку на запуск.
- [x] Проверять HTTP-ответ и результат Telegram API; не маскировать исходное падение ошибкой уведомления.
- [x] Проверить согласованные случаи без реальной отправки, затем выполнить разрешённую отправку; создать коммит.

## Фаза 7 — Jenkins

Статус: отложена в домашнее задание по решению пользователя; в текущей демонстрации не реализуется. Реализация начинается только после отдельного согласования окружения Jenkins. Наличие Jenkinsfile не означает проверку pipeline; запуск и публикация отчёта подтверждаются на реальном агенте либо остаются явно непроверенными.

### Перед реализацией уточнить

- [ ] Где находятся Jenkins и агент, доступ, ОС, label и доступные инструменты.
- [ ] Доступность Java, браузеров, драйверов и Allure Report 2 CLI 2.46.1 (Node.js проекту не нужен).
- [ ] Параметры запуска, имена Jenkins Credentials и Telegram-уведомления.
- [ ] Способ генерации и публикации Allure Report 2 (CLI с закреплённым checksum, как в GitHub Actions, или Allure Jenkins plugin).

### Реализация и проверка

- [ ] Добавить Jenkinsfile с теми же командами тестов и генерации отчёта, что локально и в GitHub Actions.
- [ ] Публиковать JUnit XML, сохранять результаты, вложения и отчёт при падениях.
- [ ] Проверить выбранный способ генерации Report 2 на реальном агенте; не предполагать наличие плагина или CLI.
- [ ] При отсутствии совместимости согласовать альтернативную генерацию и хранение отчёта.
- [ ] Не устанавливать плагины и не менять Jenkins глобально без разрешения.
- [ ] Разделить проверку Jenkinsfile и реальный запуск Jenkins; создать коммит.

## Фаза 8 — Review

Статус: завершена 2026-10-17. По решению пользователя — без изменения кода, workflow и инфраструктуры («только план»). Объём — фазы 0–5; Telegram и Jenkins исключены из review как отложенное ДЗ, а не как выполненные интеграции.

Проверенный код и workflow — commit `9799a61955dbbeacd52fbc59d199f0f17fe6d1bf` (= `ai/master`, commit успешного run 38311448403). Локальный HEAD `bb08099` отличается от него только этим файлом плана; код, workflow и wrapper идентичны — сопоставлено по `git diff`, а не по номеру HEAD. Рабочее дерево чистое: прежние whitespace-изменения `pages/SearchPage.java` и `pages/SearchResultsPage.java` убраны владельцем (см. bb08099), в review не участвовали.

### Проверено локально (2026-10-17)

- [x] Чистый checkout: `git clone` → `git checkout 9799a61` в `/tmp/phase8-review/checkout-9799a61`, изолированный `GRADLE_USER_HOME`; `reset`/`clean` и копирование build-артефактов не использовались, текущее дерево не тронуто.
- [x] Wrapper и toolchain: `./gradlew --version` сам скачал Gradle 9.6.0-bin; SHA-256 дистрибутива `bbaeb2f…529a01` и `gradle-wrapper.jar` `497c8c2a…a194a9c7` совпали с официальными (downloads.gradle.org). Java — Corretto 21.0.9. Команды: `./gradlew --version`, `./gradlew testClasses --console=plain` — BUILD SUCCESSFUL без предупреждений.
- [x] Тесты: `./gradlew test --console=plain -Dheadless=true` — 3/3 зелёных против локального Chrome 155; единственное предупреждение — CDP version mismatch (Selenium 4.49.0 поддерживает v151–153, см. риски).
- [x] Передача свойств: временный init-script и пробный тестовый класс в `/tmp` (не в репозитории) подтвердили дефолты и переопределение `baseUrl`/`browser`/`browserSize`/`headless` в JVM тестов; `selenide.browserBinary` и `webdriver.chrome.driver` доходят до `Configuration`/`System.getProperty` до открытия браузера; Selenide 7 читает `selenide.browserBinary` — подтверждено по исходникам.
- [x] Тест-код: `Selenide.open("/search")` реально использует `baseUrl`; lifecycle — конфигурация в `@BeforeEach`, `closeWebDriver()` в `@AfterEach` (сессия на тест); `sleep`, ретраев, `@Disabled`, скрытых перезапусков нет.
- [x] Allure CLI 2.46.1: скачан заново с Maven Central, SHA-256 `37428164…cbf8d` совпал с `.sha1` Maven Central и digest GitHub Release; `allure generate build/allure-results --clean -o build/allure-report` собрал отчёт.
- [x] Secrets/generated: поиск по tracked files, всей истории и CI-артефактам — секретов нет; `build/` в git не попадает; repo-level Actions variables/secrets пусты.

### Проверено в реальном GitHub Actions (без новых запусков)

- [x] Успешный run [38311448403](https://github.com/qa-guru/getting-started-java-ai/actions/runs/38311448403): headSha `9799a61`, master, jobs `ui-tests`+`deploy-report` success; Temurin 21.0.12.1, Gradle 9.6.0, CfT и ChromeDriver `153.0.8010.52` (версии совпали), Allure CLI 2.46.1 (checksum в CI совпал); BUILD SUCCESSFUL на compile и test; артефакты: 3 `*-result.json`, JUnit `tests=3 failures=0 errors=0 skipped=0`, report, github-pages.
- [x] Контролируемые падения (временные ветки, удалены): [38310722420](https://github.com/qa-guru/getting-started-java-ai/actions/runs/38310722420) — assertion-fail, артефакты с PNG-screenshot и HTML page source; [38310878425](https://github.com/qa-guru/getting-started-java-ai/actions/runs/38310878425) — compile-fail, стоп на Compile tests, report/deploy skipped; [38311003194](https://github.com/qa-guru/getting-started-java-ai/actions/runs/38311003194) — no-results, явный `::error::No Allure test results`, deploy skipped.
- [x] Workflow: все 7 actions закреплены по SHA, каждый SHA соответствует заявленному тегу; `actionlint` 1.7.12 со встроенным ShellCheck 0.11.0 — 0 ошибок; inputs валидируются (`browser` — choice `chrome`, `browserSize` — regex `^[0-9]{3,4}x[0-9]{3,4}$`); permissions минимальны на уровне jobs; exit code тестов сохраняется (`|| true`, `continue-on-error`, retries отсутствуют); `build/` не кэшируется.
- [x] Pages: последний deployment `7024504634` — SHA `9799a61` от run 38311448403; https://qa-guru.github.io/getting-started-java-ai/ — HTTP 200; распакованный артефакт `github-pages` идентичен содержимому сайта (37 файлов), отчёт показывает 3 passed; визуально проверен по скриншотам агентом — приёмка пользователем не зафиксирована.

### Findings и открытые риски

Blocker-дефектов не найдено; код не менялся. Зафиксировано:

- **Существенный риск — закрыт в фазе 9:** причина падения Chrome подтверждена (AppArmor-блокировка unprivileged user namespaces для CfT на ubuntu-24.04; точное сообщение `No usable sandbox!` — см. фазу 9). `--no-sandbox` убран; вместо него AppArmor-профиль для бинаря CfT — sandbox включён.
- **Закрыто в фазе 9 (решение пересмотрено):** publish-always — failed-отчёт с master публиковался на публичный Pages (run `38309080672`); с фазы 9 публикация только при зелёных тестах (`needs.ui-tests.result == 'success'` + `steps.tests.outcome == 'success'` на staging-артефакте).
- **Закрыто в фазе 9:** CfT и ChromeDriver обновлены до `155.0.8059.84` (Stable на день выполнения); Selenide 7.19.0 → Selenium 4.51.0 поддерживает CDP v153–v155 — version-mismatch warning устранён и локально, и в CI.
- **Закрыто в фазе 9:** `build/allure-results` очищается перед каждым прогоном (`doFirst` в test task); два локальных прогона → ровно 3 `*-result.json`.
- **Закрыто в фазе 9 (частично):** `default_workflow_permissions` write→read, `can_approve_pull_request_reviews` true→false через API. `allowed_actions=all` и `sha_pinning_required=false` не менялись (workflow использует сторонний browser-actions/setup-chrome; смена `allowed_actions` требует allowlist) — открытый пункт фазы 9.
- **Закрыто в фазе 9:** `cache-provider: enhanced` — proprietary default setup-gradle v6.4.0 (виден в логе как «Enhanced Caching…»); явно закреплён open-source `basic` — в логе run 39287982359 «Basic Caching».
- **Риск (принят):** зависимость от живого github.com — данные `qa.guru`, семантика `stars:>999999999`, возможные HTTP 429; без ретраев. Фаза 9 наблюдала единичный flake: GitHub отдал страницу-подсказку вместо результатов для `stars:<0` (прошло при немедленном повторе без изменений — транзиентное поведение GitHub, не браузера/стека).

### Непроверенное

- Сценарий «ошибка генерации при сохранённых сырых результатах» — подходящего run в истории нет; без нового запуска не воспроизведён.
- Публикация failed-отчёта после контролируемого падения на default branch — наблюдалось только неконтролируемое (`38309080672`); на временных ветках deploy не настроен.
- Dispatch с невалидным `browserSize` и поведение `timeout-minutes` относительно загрузки артефактов — только по коду.
- Настоящая причина sandbox-падения Chrome в CI — диагностический run не согласован и не выполнялся.
- Интерактивная визуальная приёмка отчёта пользователем; macOS/Windows-специфика runner'ов.

## Фаза 9 — Доработка findings финального review

Статус: завершена 2026-10-19; итоговые изменения проверены, push на ai/master — после показа результатов и подтверждения пользователя.

### Задача 1 — sandbox-диагностика (run [39286924890](https://github.com/qa-guru/getting-started-java-ai/actions/runs/39286924890), ветка ci-check/sandbox-diag)

Временный workflow `.github/workflows/sandbox-diag.yml` (только на ветке, в master не входил) прогонял CfT напрямую с полным stderr и проверял гипотезу AppArmor. Факты с ubuntu-24.04 runner:

- `kernel.apparmor_restrict_unprivileged_userns = 1`; `unshare --user --map-root-user true` → BLOCKED; 123 AppArmor-профиля загружено, для CfT-пути профиля нет.
- CfT 153.0.8010.52 без `--no-sandbox`: exit 134, FATAL `No usable sandbox! ... Ubuntu 23.10+ ... AppArmor` (zygote_host_impl_linux.cc:129) — настоящая причина установлена, не «Chrome instance exited».
- Контроль: предустановленный `/opt/google/chrome/chrome` работает (exit 0) — у него есть профиль `/etc/apparmor.d/chrome`.
- `chrome_sandbox` подтверждён в листинге архива CfT (имя с подчёркиванием — finding фазы 8 верен).

Проверенные альтернативы `--no-sandbox` (все по документации Chromium apparmor-userns-restrictions.md):

| Вариант | Суть | Результат |
|---|---|---|
| A | setuid `chrome_sandbox` из архива CfT + `CHROME_DEVEL_SANDBOX` | exit 0, DOM отрендерен |
| B | `CHROME_DEVEL_SANDBOX=/opt/google/chrome/chrome-sandbox` (стоковый helper) | exit 134 — у файла на runner нет setuid-бита (`-rwxrwxrwx`) |
| C | AppArmor-профиль `userns` для бинаря CfT + `apparmor_parser -r` | exit 0, DOM отрендерен |
| D | `sysctl kernel.apparmor_restrict_unprivileged_userns=0` (контроль гипотезы) | exit 0 |

Итог: причина подтверждена — AppArmor-ограничение unprivileged userns для CfT. Выбран вариант C (AppArmor-профиль): сохраняет современный userns-сандбокс, тот же механизм, что у штатно установленного Chrome на Ubuntu 24.04; вариант A зафиксирован как проверенный запасной. `--no-sandbox` удалён из workflow; компромисс снят, переносить его на локальные запуски/Jenkins не требуется и не делается.

Подтверждение на реальном workflow: run [39287273490](https://github.com/qa-guru/getting-started-java-ai/actions/runs/39287273490) (Chrome 153, без `--no-sandbox`, с профилем) — ui-tests success, 3/3.

### Задача 2 — обновление стека

- Selenide 7.18.2 → 7.19.0 (релиз 2026-10-10, Maven Central): тянет Selenium 4.51.0 (релиз 2026-10-09) с `selenium-devtools` v153/v154/v155. `allure-selenide`/`allure-jupiter` 3.0.0 и AspectJ 1.9.25 без изменений — совместимость по декларациям (allure-selenide нацелен на Selenide 7.x) и по фактическим прогонам.
- CfT + ChromeDriver 153.0.8010.52 → 155.0.8059.84 — Stable по last-known-good-versions.json на 2026-10-19; совпадает с локальным Chrome 155.0.8059.84; версии браузера и драйвера равны.
- Проверки: локально `./gradlew test -Dheadless=true` — 3/3, CDP-warning исчез; CI run [39287982359](https://github.com/qa-guru/getting-started-java-ai/actions/runs/39287982359) — зелёный (обе версии 155.0.8059.84 подтверждены логом).

### Задача 3 — правки workflow

- Pages публикуется только при зелёных тестах: `deploy-report` требует `needs.ui-tests.result == 'success'`; staging-артефакт Pages пропускается при падении тестов (`steps.tests.outcome == 'success'`). Решение publish-always фазы 5 отменено и зафиксировано здесь.
- `cache-provider: basic` явно закреплён — default setup-gradle v6.4.0 `enhanced` (proprietary, виден в логе 39287273490); в run 39287982359 — «Basic Caching».
- `--no-sandbox` снят по итогам задачи 1; вместо него шаг «Allow user namespaces for Chrome for Testing».
- Непроверенное (ограничение зафиксировано): условие публикации завязано на default branch — skip при падении на временной ветке не проверяется, ломающий push в master ради проверки не выполнялся. Проверено: code review, actionlint 1.7.12 (0 ошибок), зелёные run'ы 39287273490 и 39287982359.

### Задача 4 — репозиторий и build.gradle

- `PUT /repos/qa-guru/getting-started-java-ai/actions/permissions/workflow` (HTTP 204): `default_workflow_permissions` write→read, `can_approve_pull_request_reviews` true→false; перечитано GET — значения применены. `allowed_actions=all` и `sha_pinning_required=false` сознательно не менялись: workflow использует сторонний `browser-actions/setup-chrome`, `allowed_actions` требует allowlist — остаётся открытым пунктом.
- build.gradle: в `test` добавлено `doFirst { delete layout.buildDirectory.dir('allure-results') }`. Проверка: при старте было 10 `*-result.json` от прошлых прогонов → после прогона 3; второй реальный прогон (`--rerun-tasks`) → снова ровно 3 `*-result.json`; up-to-date-прогон без выполнения тестов директорию не трогает.

### Задача 5 — завершение

- Коммиты: `ef7abad` (AppArmor-профиль вместо `--no-sandbox`), `898051a` (Selenide 7.19.0 + CfT 155), `7723eaa` (publish-on-green + cache-provider basic), `cead8c5` (очистка allure-results), плюс коммит плана. Запушены на ai/master; временная ветка ci-check/sandbox-diag удалена локально и на remote; `sandbox-diag.yml` в master не входит.
- Дочистка после merge: осиротевшие workflow `Probe` (остаток фазы 5) и `Sandbox diagnostics` отключены через API (state `disabled_manually` — файлов нет ни на одной ветке; API не позволяет удалить запись workflow из списка Actions); из environment `github-pages` удалена stale branch-policy `main` (ветки не существует), осталась только `master`; локальные диагностические файлы в /tmp удалены.
- Проверки перед отчётом: `actionlint` 0 ошибок, `git diff --check` чисто, локальный `./gradlew test -Dheadless=true` 3/3 без CDP-warning.
- Проверено в реальном CI: runs 39286924890 (диагностика), 39287273490 (фикс на 153), 39287982359 (полный набор на 155) — зелёные; после push — run [39288818070](https://github.com/qa-guru/getting-started-java-ai/actions/runs/39288818070) на master: ui-tests и deploy-report success, https://qa-guru.github.io/getting-started-java-ai/ — HTTP 200, `widgets/summary.json` passed=3/total=3. Не проверено: skip деплоя при падении на master (ломающий push намеренно не выполнялся — ограничение из задачи 3), визуальная приёмка отчёта пользователем.

### Открытые пункты после фазы 9

- `allowed_actions`/`sha_pinning_required` на уровне репозитория — сузить (allowlist + sha_pinning_required=true) при следующем согласовании; workflow уже закреплён по SHA на уровне файла.
- Визуальная приёмка обновлённого Pages-отчёта после первого зелёного run на master.
- Фазы 6–7 — домашнее задание, не реализуются.

## Базовые команды проверки

Команды выполняются из корня Git-репозитория. По отчёту фазы 3 полный набор из трёх тестов проверен с defaults и в headless после восстановления доступности GitHub. Эти результаты не гарантируют доступность внешнего сайта при следующем запуске.

```bash
./gradlew --version
./gradlew test --rerun-tasks --console=plain
./gradlew test -Dheadless=true -DbrowserSize=1366x768 --rerun-tasks --console=plain
allure --version
allure generate build/allure-results --clean -o build/allure-report
allure open build/allure-report
git diff --check
```

При изменении только этого файла достаточно проверить содержимое Markdown, актуальность статусов, whitespace и состав коммита; UI-тесты ради изменения плана запускать не требуется.

## Критерий завершения фазы

1. Выполнен именно согласованный объём.
2. Проверки действительно запущены и результаты зафиксированы.
3. Временная диагностика удалена, ограничения и блокеры перечислены.
4. Этот план обновлён без превращения предположений в подтверждённые результаты.
5. Свои изменения закоммичены; чужой WIP не затронут.
6. Работа остановлена до подтверждения следующей фазы.
