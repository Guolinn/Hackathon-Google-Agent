# CrisisFlow AI PRD

版本：Hackathon MVP v1.0
项目名称：CrisisFlow AI
产品类型：AI-powered Emergency Medical Supply Coordination Platform
核心场景：湾区山火后的医疗资源缺口预测与应急调拨
推荐 MCP：Fivetran MCP

---

## 1. 一句话说明

CrisisFlow AI 是一个面向灾害应急场景的医疗供应链调度 AI Agent。灾害发生后，它会预测未来数小时的伤员规模与医疗资源缺口，检查医院药品、床位、人力是否足够；如果不足，自动查询城市预认证供应商、周边医院和仓储节点的可用资源，对比 ETA、路线风险和库存，生成可审批的调拨方案，并通过平台向供应商、医院和物流方发起调拨请求。

核心原则：

- AI 负责分析、推荐、解释、生成调拨方案。
- 指挥官或政府应急中心负责审批。
- 平台负责发出正式调拨请求并记录审计日志。
- 供应商、医院、物流方负责确认和执行。

---

## 2. 产品定位

### 2.1 我们不是做什么

本项目不是：

- 不是山火检测系统。
- 不是消防指挥系统。
- 不是普通聊天机器人。
- 不是完整政府灾害管理平台。
- 不是真实医院 ERP 或药企系统替代品。
- 不是让 AI 自动绕过人类审批去调配医疗资源。

### 2.2 我们要做什么

本项目要做的是：

- 在灾害发生后，快速预测医疗资源压力。
- 判断本地医院是否会出现药品、床位、人力短缺。
- 查询预认证供应商和周边医院资源。
- 对比库存、ETA、路线风险、成本、合约状态。
- 生成可解释、可审批的调拨建议。
- 审批后通过平台发送 Emergency Dispatch Request。
- 如果供应商系统没有接入，则自动使用邮件、短信、电话等 fallback 联系紧急负责人。

### 2.3 Hackathon 版本的重点

Hackathon MVP 不需要真实接入政府、医院、药企数据库。我们使用模拟数据，但模拟数据必须像真实业务数据。

展示重点：

- Agent 真的会查数据。
- Agent 真的会计算缺口。
- Agent 真的会比较不同供应来源和 ETA。
- Agent 真的会生成审批单和 briefing。
- 数据整合逻辑能自然解释为什么选择 Fivetran MCP。

---

## 3. 目标用户

### 3.1 主用户

Emergency Operations Center Coordinator
应急指挥中心协调员

核心任务：

- 判断灾害对医疗系统的压力。
- 快速知道哪些资源会短缺。
- 确定从哪里调货、调多少、多久到。
- 将关键调度提交给政府或应急中心审批。
- 向医院、供应商、物流方发送正式协调请求。

### 3.2 次用户

Health Department Approver
卫生部门审批人

关注：

- 调拨是否必要。
- 是否影响其他区域医疗资源。
- 是否符合应急授权规则。

Hospital Coordinator
医院协调员

关注：

- 本院预计接收多少伤员。
- 哪些药品、床位、人力不足。
- 是否需要分流或接收转运患者。

Supplier Emergency Contact
供应商紧急联系人

关注：

- 是否收到正式调拨请求。
- 需要提供什么物资、数量、目的地。
- 是否能准时出库和运输。

Logistics Coordinator
物流协调员

关注：

- 从哪里取货。
- 送到哪里。
- 哪条路线可行。
- ETA 和路线风险。

---

## 4. 核心 Demo 场景

### 4.1 场景名称

Marin Wildfire Medical Surge

### 4.2 故事背景

Marin County 发生快速蔓延的山火。风向向东南偏移，烟雾进入 San Francisco。Highway 101 出现严重拥堵，部分撤离车辆和救护车受阻。SF General 预计在 2.5 小时内接收大量烧伤和吸入性损伤患者。

CrisisFlow AI 接收到灾情信号后，自动整合 incident feed、天气、交通、医院资源、供应商库存和物流 ETA 数据，预测医疗资源缺口，并生成可审批的调拨方案。

### 4.3 Demo 主线

From Incident Alert to Approved Medical Dispatch Plan in 5 Minutes

完整流程：

1. 灾害事件进入系统。
2. Agent 分析灾情和未来几小时医疗压力。
3. Agent 检查医院药品、床位、人力。
4. Agent 发现资源缺口。
5. Agent 查询城市预认证供应商网络。
6. Agent 对比库存、ETA、路线风险和合同状态。
7. Agent 推荐调拨方案。
8. 指挥官审批。
9. 平台发送 Emergency Dispatch Request。
10. 供应商确认，Agent 更新状态并生成 briefing。

---

## 5. 核心价值主张

### 5.1 对政府应急中心

帮助应急中心在灾害发生后的关键几分钟内，从混乱、分散的数据中得到可执行方案。

### 5.2 对医院

提前知道预计患者数量和资源缺口，避免伤员到达后才发现药品、床位或医护不足。

### 5.3 对供应商

提前加入城市预认证应急供应网络，灾时收到结构化、可追踪的正式调拨请求。

### 5.4 对比赛评委

这是一个真正的 agent workflow：

- 多数据源整合。
- 多步骤工具调用。
- 资源缺口计算。
- 方案排序。
- 人类审批。
- 自动 briefing 和 dispatch request。

---

## 6. 推荐 MCP 选择

### 6.1 主推荐：Fivetran MCP

选择理由：

CrisisFlow 的核心问题是 emergency data fragmentation。医院、供应商、仓库、物流、交通、灾情数据都在不同系统中。Fivetran 的价值正好是把多源数据同步到 BigQuery、Cloud SQL 或 Cloud Storage，形成 Agent 可查询的统一数据层。

在 Demo 中，我们可以这样讲：

> For the hackathon, we use simulated hospital, supplier, traffic, and incident datasets. In production, Fivetran would connect these fragmented operational systems into BigQuery, giving the Gemini-powered agent a unified emergency decision layer.

### 6.2 为什么不是优先选 Arize

Arize Phoenix 适合做 agent tracing 和 observability，可以作为加分项。但它不是本项目的核心业务能力。核心业务能力是跨系统找资源并调度。

### 6.3 为什么不是优先选 Elastic

Elastic 适合搜索大量文档、政策、地理信息和历史事件记录。如果项目重点是“应急知识检索”，Elastic 很合适。但本项目重点是结构化库存、床位、ETA 和供应链调度，所以 Fivetran 更贴合。

### 6.4 为什么不是优先选 MongoDB

MongoDB 可以做数据库，但本项目真正要展示的是“从多个系统接入数据”，而不是只存一份数据。

---

## 7. 产品模块总览

### 7.1 Command Center

应急指挥主工作台，展示灾害事件、地图态势、关键风险、Agent 状态和资源概览。

### 7.2 Incident Intelligence

灾情感知与影响预测模块，预测伤员规模、伤员类型、影响区域和高峰时间。

### 7.3 Resource Gap Analysis

医疗资源缺口分析模块，检查药品、床位、医护、设备是否足够。

### 7.4 Supplier Network

城市预认证供应商网络，维护医院、供应商、仓库、物流方和紧急联系人。

### 7.5 Dispatch Planner

调拨方案生成模块，对比不同来源的库存、ETA、路线风险和成本。

### 7.6 Approval Workflow

审批流模块，确保所有关键调度动作在执行前经过应急中心或政府部门授权。

### 7.7 Emergency Dispatch Request

审批后由平台发送给供应商、医院或物流方的正式调拨请求。

### 7.8 Briefing Generator

自动生成 EOC briefing、市长简报、公众提醒、医院协调 memo 和供应商通知。

---

## 8. 页面 PRD

Hackathon MVP 建议做 6 个页面或状态。不要做 landing page，打开就是 Command Center。

---

### Page 1: Command Center

#### 页面目标

让评委在 10 秒内看懂：

- 发生了什么灾害。
- 哪些地方有风险。
- 预计会有多少伤员。
- 医疗资源是否紧张。
- Agent 正在做什么。

#### 页面布局

顶部：Incident Summary Bar
左侧：Map / Situational View
右侧：AI Agent Panel
底部：Operational Data Tabs

#### 顶部信息

字段：

- Incident: Marin Wildfire
- Severity: Level 4
- Location: Marin County
- Wind Direction: South-East toward SF
- Population at Risk: 42,000
- Projected Patients: 180
- Hospital Pressure: High
- Resource Gaps: 5
- Approval Required: 4 actions

#### 地图区域展示

地图可以是 mock map，不需要真实 GIS。

显示元素：

- 火灾点位。
- 烟雾影响区域。
- 风向箭头。
- Highway 101 拥堵。
- SF General、UCSF、CPMC、Oakland Medical Center。
- MedSupply Oakland、NorCal Oxygen、San Jose Warehouse。
- 推荐运输路线。

#### AI Agent Panel

Agent 状态步骤：

- Incident received
- Weather and wind data checked
- Traffic conditions checked
- Hospital capacity checked
- Medical inventory checked
- Supplier network queried
- ETA options ranked
- Dispatch plan ready

按钮：

- Generate Response Plan
- View Resource Gaps
- Open Approval Queue

#### 底部 Tabs

Tabs：

- Hospitals
- Supplies
- Suppliers
- Traffic
- Approvals

Hospital tab 示例：

| Hospital | ER Status | Burn Beds | ICU Beds | Pressure |
|---|---:|---:|---:|---|
| SF General | Critical | 3/8 | 7/12 | High |
| UCSF | Stable | 5/6 | 9/14 | Medium |
| CPMC | Stable | 2/4 | 6/10 | Medium |
| Oakland Medical | Available | 4/5 | 8/11 | Low |

#### Demo 展示方式

进入页面时，先让 Agent Panel 显示正在分析。几秒后出现红色风险卡片：

- SF General burn kits shortage expected in 2.1h
- Highway 101 congestion may delay ambulance routes by 38m
- Respiratory medication demand exceeds local inventory by 120 doses

---

### Page 2: Incident Detail Drawer

#### 页面目标

解释 Agent 为什么认为这是一个大事件，以及为什么需要触发医疗资源调度。

#### 触发方式

从 Command Center 点击 Incident Summary 或地图上的 wildfire marker，打开右侧 drawer。

#### 内容结构

Section 1: Event Details

- Incident ID: INC-2026-0529-MARIN-014
- Type: Wildfire
- Location: Marin County
- Detected At: 17:12
- Source: Emergency incident feed
- Severity: Level 4

Section 2: Environmental Context

- Wind Speed: 24 mph
- Wind Direction: South-East
- Air Quality Trend: Deteriorating
- Smoke Direction: Toward San Francisco
- Nearby Risk: Elderly communities, schools, Highway 101 corridor

Section 3: Population Impact

- Population at Risk: 42,000
- High-risk residents: 8,600
- Evacuation Zone A: 12,000
- Evacuation Zone B: 18,000
- Projected first patient wave: 180

Section 4: Patient Surge Estimate

| Patient Type | Estimated Count | Primary Need |
|---|---:|---|
| Burns | 35 | Burn kits, dressings, pain medication |
| Smoke inhalation | 80 | Albuterol, oxygen, respiratory beds |
| Trauma | 28 | ER beds, imaging, trauma staff |
| ICU risk | 12 | ICU beds, ventilators |
| Observation | 25 | General beds, monitoring |

#### Agent Conclusion 文案

> CrisisFlow classifies this incident as Level 4 because projected patient surge exceeds SF General's current burn and respiratory treatment capacity within the next 2.5 hours.

---

### Page 3: Resource Gap Analysis

#### 页面目标

这是产品核心页面。它要证明 Agent 不是在聊天，而是在用数据计算资源缺口。

#### 页面结构

左侧：Resource Gap Table
右侧：Hospital Pressure Cards
底部：Agent Reasoning Summary

#### Resource Gap Table

| Resource | Needed | Available | Gap | Time to Shortage | Severity |
|---|---:|---:|---:|---:|---|
| Burn kits | 420 | 180 | 240 | 2.1h | Critical |
| Albuterol doses | 300 | 180 | 120 | 1.8h | Critical |
| Oxygen cylinders | 90 | 54 | 36 | 2.6h | High |
| ICU beds | 12 | 7 | 5 | 3.0h | High |
| ER nurses | 28 | 20 | 8 | 2.4h | Medium |

#### Hospital Pressure Cards

SF General:

- Projected patients: 105
- Current ER load: 86%
- Burn kit gap: 240
- Respiratory medication gap: 120
- Status: Critical

UCSF:

- Projected patients: 35
- Respiratory beds available: 8
- Albuterol stock available: 150
- Status: Can absorb overflow

CPMC:

- Projected patients: 25
- General ER capacity available
- Status: Good for low-acuity diversion

Oakland Medical Center:

- Projected patients: 15
- Burn treatment capacity available
- Status: Backup receiving site

#### Agent Reasoning Summary

文案：

> SF General will exceed burn and respiratory treatment capacity before the second patient wave. CrisisFlow recommends immediate supply transfer and patient diversion to reduce overload risk.

#### Demo 展示方式

点击 `View Resource Gaps` 后，页面自动高亮三个缺口：

- Burn kits
- Albuterol
- Oxygen cylinders

然后 Agent 进入下一步：Find Nearby Resources。

---

### Page 4: Supplier Network

#### 页面目标

展示每个城市平时就维护一套预认证应急供应商网络。灾害发生时，Agent 不是全网乱搜，而是在可信供应网络里查库存、合同、ETA 和紧急联系人。

#### 页面结构

顶部：Network Summary
中间：Supplier Table
右侧：Selected Supplier Detail

#### Network Summary

- City Network: San Francisco Bay Area
- Active Suppliers: 18
- Connected by API: 7
- Portal-only Suppliers: 6
- Emergency Contact Fallback: 5
- Average Response SLA: 45 min

#### Supplier Table

| Supplier | Type | Location | Stock Match | SLA | Integration | Status |
|---|---|---|---:|---:|---|---|
| MedSupply Oakland | Burn care supplies | Oakland | 300 burn kits | 45m | API | Active |
| UCSF Storage | Hospital reserve | SF | 150 albuterol | 25m | Database | Active |
| NorCal Oxygen | Oxygen supplier | San Jose | 80 cylinders | 90m | Email fallback | Active |
| BayMed Logistics | Medical transport | Bay Area | 6 vehicles | 30m | Portal | Active |
| Sacramento MedDepot | General supplies | Sacramento | 900 burn kits | 140m | API | Backup |

#### Selected Supplier Detail

MedSupply Oakland:

- Contract status: Pre-approved emergency vendor
- Available burn kits: 300
- Earliest pickup: 18:05
- Estimated delivery: 42 min
- Contact method: API
- Backup contact: operations@medsupply-oakland.example
- SLA: 45 min regional emergency dispatch

#### Demo 展示方式

Agent 发现 burn kits 缺口后，打开 Supplier Network 页面，高亮 MedSupply Oakland，因为它库存足够且 ETA 最优。

---

### Page 5: Dispatch Plan

#### 页面目标

展示 Agent 如何把资源缺口转化成可执行调拨方案。

#### 页面结构

顶部：Recommended Plan Summary
中间：Dispatch Recommendation Cards
底部：ETA Comparison Table

#### Recommended Plan Summary

- Plan ID: PLAN-2026-0529-014
- Objective: Cover critical medical shortages before second patient wave
- Total actions: 5
- Approval required: Yes
- Estimated time to stabilize: 2.5h
- Risk reduction: High

#### Dispatch Recommendation Cards

Card 1:

Title: Transfer 300 burn kits from MedSupply Oakland to SF General

- Quantity: 300
- ETA: 42 min
- Route: I-580 to Bay Bridge to Mission St
- Why: SF General has a 240-unit burn kit gap
- Expected impact: Covers projected burn care demand for 6 hours
- Risk if delayed: Burn care shortage before second patient wave
- Approval required: Health Department
- Confidence: High

Card 2:

Title: Transfer 150 albuterol doses from UCSF Storage to SF General

- Quantity: 150
- ETA: 28 min
- Route: Local medical courier
- Why: Respiratory medication gap reaches 120 doses in 1.8h
- Expected impact: Covers smoke inhalation surge
- Risk if delayed: Increased respiratory treatment wait times
- Approval required: Hospital coordination
- Confidence: High

Card 3:

Title: Dispatch 40 oxygen cylinders from NorCal Oxygen to SF General

- Quantity: 40
- ETA: 91 min
- Route: US-101 alternative via I-280
- Why: Oxygen cylinder gap reaches 36 units in 2.6h
- Expected impact: Covers severe smoke inhalation cases
- Risk if delayed: Oxygen shortage during ICU surge
- Approval required: Health Department
- Confidence: Medium

Card 4:

Title: Divert low-acuity patients to CPMC and UCSF

- Quantity: 45 patients
- ETA effect: Reduces SF General ER pressure by 18%
- Why: SF General is nearing ER overload
- Approval required: EOC and hospital coordination
- Confidence: High

Card 5:

Title: Place BayMed Logistics on standby for supplier pickup

- Vehicles: 3
- ETA to pickup: 30 min
- Why: Highway 101 congestion may delay standard delivery routes
- Approval required: EOC logistics lead
- Confidence: Medium

#### ETA Comparison Table

| Source | Resource | Available | ETA | Route Risk | Contract | Recommendation |
|---|---|---:|---:|---|---|---|
| MedSupply Oakland | Burn kits | 300 | 42m | Medium | Pre-approved | Best |
| UCSF Storage | Albuterol | 150 | 28m | Low | Hospital reserve | Best for respiratory meds |
| NorCal Oxygen | Oxygen | 80 | 91m | Low | Pre-approved | Best oxygen source |
| Sacramento MedDepot | Burn kits | 900 | 138m | Medium | Pre-approved | Backup |
| San Jose Warehouse | Mixed supplies | 600 | 104m | Low | Portal only | Backup |

#### Demo 展示方式

这是 demo 高潮。Agent 生成计划后，页面应该明显展示：

- 推荐方案。
- 为什么推荐。
- ETA 对比。
- 哪些需要审批。

---

### Page 6: Approval and Dispatch

#### 页面目标

展示 AI 不直接执行高风险调度，而是提交给人类审批。审批后由平台发出正式调拨请求。

#### 页面结构

左侧：Approval Queue
右侧：Dispatch Request Preview
底部：Briefing Generator

#### Approval Queue

| Action | Owner | Risk | Status |
|---|---|---|---|
| Transfer burn kits from Oakland | Health Department | High | Pending |
| Transfer albuterol from UCSF | Hospital Coordination | Medium | Pending |
| Dispatch oxygen cylinders | Health Department | High | Pending |
| Divert low-acuity patients | EOC | High | Pending |
| Notify supplier network | EOC | Medium | Pending |

每条 action 按钮：

- Approve
- Request changes
- Reject

#### Dispatch Request Preview

Request ID: EDR-2026-0529-014-A
Supplier: MedSupply Oakland
Destination: SF General
Item: Burn kits
Quantity: 300
Required arrival: 19:05
Authorization: Health Department emergency approval
Contact method: API
Backup method: Email + SMS
Backup supplier: Sacramento MedDepot

Request message:

> Emergency Dispatch Request: Please release 300 burn kits to SF General under emergency authorization EOC-2026-0529-014. Required arrival before 19:05. Confirm availability and pickup readiness within 10 minutes.

#### 审批后状态

点击 Approve Dispatch Plan 后：

- Status changes from Pending to Approved.
- Dispatch Request Sent.
- Supplier Status: Awaiting confirmation.
- Then change to Accepted.
- ETA appears on map.

#### Briefing Generator

按钮：

- Generate EOC Briefing
- Generate Mayor Briefing
- Generate Supplier Alert
- Generate Public Advisory

EOC Briefing 示例：

> Marin wildfire smoke impact is expected to drive a 180-patient surge over the next 2.5 hours. SF General is projected to exceed burn and respiratory treatment capacity. CrisisFlow recommends transferring 300 burn kits from MedSupply Oakland, 150 albuterol doses from UCSF Storage, and 40 oxygen cylinders from NorCal Oxygen. Low-acuity patients should be diverted to CPMC and UCSF. All high-risk actions require EOC and Health Department approval before dispatch.

Public Advisory 示例：

> Smoke conditions are worsening across parts of San Francisco. Residents in affected areas should limit outdoor activity, follow evacuation instructions, and keep emergency routes clear. Additional medical resources are being coordinated across regional hospitals and suppliers.

#### Demo 展示方式

一定要强调：

> AI recommends. Humans approve. CrisisFlow dispatches.

---

## 9. 数据设计

Hackathon 版本使用 mock data。建议把 mock data 放在 CSV、Google Sheets、Postgres 或本地 JSON 中，再同步或模拟同步到 BigQuery。

### 9.1 数据总流

Mock source data -> Fivetran -> BigQuery -> Agent tools -> Response plan -> Approval -> Dispatch request -> Briefing

### 9.2 表结构

#### Table: incidents

用途：灾害事件基本信息。

| Field | Type | Example |
|---|---|---|
| incident_id | STRING | INC-2026-0529-MARIN-014 |
| type | STRING | wildfire |
| location_name | STRING | Marin County |
| latitude | FLOAT | 37.9577 |
| longitude | FLOAT | -122.5311 |
| severity | STRING | Level 4 |
| detected_at | TIMESTAMP | 2026-05-29T17:12:00 |
| population_at_risk | INTEGER | 42000 |
| status | STRING | active |

#### Table: weather_conditions

用途：风速、风向、气候条件。

| Field | Type | Example |
|---|---|---|
| incident_id | STRING | INC-2026-0529-MARIN-014 |
| wind_speed_mph | FLOAT | 24 |
| wind_direction | STRING | South-East |
| temperature_f | FLOAT | 82 |
| humidity_percent | FLOAT | 21 |
| air_quality_index | INTEGER | 168 |
| smoke_direction | STRING | toward_san_francisco |

#### Table: traffic_routes

用途：道路状态与 ETA。

| Field | Type | Example |
|---|---|---|
| route_id | STRING | ROUTE-OAK-SFGH-001 |
| origin | STRING | MedSupply Oakland |
| destination | STRING | SF General |
| route_name | STRING | I-580 -> Bay Bridge -> Mission St |
| normal_eta_min | INTEGER | 32 |
| current_eta_min | INTEGER | 42 |
| congestion_level | STRING | medium |
| route_risk | STRING | medium |
| blocked | BOOLEAN | false |

#### Table: hospitals

用途：医院基础信息。

| Field | Type | Example |
|---|---|---|
| hospital_id | STRING | HOSP-SFGH |
| name | STRING | SF General |
| city | STRING | San Francisco |
| latitude | FLOAT | 37.7557 |
| longitude | FLOAT | -122.4044 |
| trauma_level | STRING | Level 1 |
| burn_unit | BOOLEAN | true |
| emergency_contact | STRING | sfgh-coordination@example.org |

#### Table: hospital_capacity

用途：医院床位和接收能力。

| Field | Type | Example |
|---|---|---|
| hospital_id | STRING | HOSP-SFGH |
| er_capacity_total | INTEGER | 120 |
| er_capacity_available | INTEGER | 17 |
| icu_beds_total | INTEGER | 12 |
| icu_beds_available | INTEGER | 7 |
| burn_beds_total | INTEGER | 8 |
| burn_beds_available | INTEGER | 3 |
| respiratory_beds_available | INTEGER | 6 |
| updated_at | TIMESTAMP | 2026-05-29T17:20:00 |

#### Table: hospital_inventory

用途：医院药品与医疗物资库存。

| Field | Type | Example |
|---|---|---|
| hospital_id | STRING | HOSP-SFGH |
| item_id | STRING | ITEM-BURN-KIT |
| item_name | STRING | Burn kit |
| category | STRING | burn_care |
| quantity_available | INTEGER | 180 |
| reorder_threshold | INTEGER | 250 |
| unit | STRING | kit |
| updated_at | TIMESTAMP | 2026-05-29T17:20:00 |

#### Table: hospital_staffing

用途：医院医护人力。

| Field | Type | Example |
|---|---|---|
| hospital_id | STRING | HOSP-SFGH |
| role | STRING | ER nurse |
| staff_available | INTEGER | 20 |
| staff_needed_projected | INTEGER | 28 |
| shift_end | TIMESTAMP | 2026-05-29T23:00:00 |

#### Table: suppliers

用途：预认证供应商基础信息。

| Field | Type | Example |
|---|---|---|
| supplier_id | STRING | SUP-OAK-MED |
| name | STRING | MedSupply Oakland |
| type | STRING | burn_care_supplier |
| city | STRING | Oakland |
| latitude | FLOAT | 37.8044 |
| longitude | FLOAT | -122.2712 |
| integration_type | STRING | API |
| contract_status | STRING | pre_approved |
| emergency_sla_min | INTEGER | 45 |
| primary_contact | STRING | ops@medsupply-oakland.example |
| backup_contact | STRING | emergency@medsupply-oakland.example |
| status | STRING | active |

#### Table: supplier_inventory

用途：供应商库存。

| Field | Type | Example |
|---|---|---|
| supplier_id | STRING | SUP-OAK-MED |
| item_id | STRING | ITEM-BURN-KIT |
| item_name | STRING | Burn kit |
| quantity_available | INTEGER | 300 |
| earliest_pickup_min | INTEGER | 20 |
| unit | STRING | kit |
| updated_at | TIMESTAMP | 2026-05-29T17:24:00 |

#### Table: transport_options

用途：物流能力。

| Field | Type | Example |
|---|---|---|
| transport_id | STRING | TRANS-BAYMED-001 |
| provider_name | STRING | BayMed Logistics |
| vehicle_type | STRING | medical_van |
| vehicles_available | INTEGER | 6 |
| cold_chain | BOOLEAN | false |
| pickup_eta_min | INTEGER | 30 |
| status | STRING | active |

#### Table: approval_requests

用途：审批请求。

| Field | Type | Example |
|---|---|---|
| approval_id | STRING | APR-2026-0529-001 |
| incident_id | STRING | INC-2026-0529-MARIN-014 |
| action_type | STRING | supply_transfer |
| action_summary | STRING | Transfer 300 burn kits to SF General |
| required_approver | STRING | Health Department |
| risk_level | STRING | High |
| status | STRING | pending |
| created_at | TIMESTAMP | 2026-05-29T17:35:00 |

#### Table: emergency_contacts

用途：没有 API 接入时的 fallback 联系人。

| Field | Type | Example |
|---|---|---|
| contact_id | STRING | CONTACT-OAK-MED-001 |
| organization_id | STRING | SUP-OAK-MED |
| name | STRING | Emergency Ops Desk |
| role | STRING | Dispatch Manager |
| email | STRING | ops@medsupply-oakland.example |
| phone | STRING | +1-555-0101 |
| preferred_channel | STRING | email_sms |
| available_24_7 | BOOLEAN | true |

---

## 10. Mock 数据建议

### 10.1 Incident

- Incident: Marin Wildfire
- Severity: Level 4
- Population at risk: 42,000
- Projected patients: 180
- First wave arrival: 2.5 hours

### 10.2 Patient Estimate

| Patient Type | Count |
|---|---:|
| Burns | 35 |
| Smoke inhalation | 80 |
| Trauma | 28 |
| ICU risk | 12 |
| Observation | 25 |

### 10.3 Resource Demand

| Resource | Demand Formula | Needed |
|---|---|---:|
| Burn kits | Burns * 12 | 420 |
| Albuterol | Smoke inhalation * 3.75 | 300 |
| Oxygen cylinders | Severe respiratory cases * 3 | 90 |
| ICU beds | ICU risk | 12 |
| ER nurses | Projected patients / 6.5 | 28 |

### 10.4 Current SF General Supply

| Resource | Available |
|---|---:|
| Burn kits | 180 |
| Albuterol | 180 |
| Oxygen cylinders | 54 |
| ICU beds | 7 |
| ER nurses | 20 |

### 10.5 Calculated Gap

| Resource | Needed | Available | Gap |
|---|---:|---:|---:|
| Burn kits | 420 | 180 | 240 |
| Albuterol | 300 | 180 | 120 |
| Oxygen cylinders | 90 | 54 | 36 |
| ICU beds | 12 | 7 | 5 |
| ER nurses | 28 | 20 | 8 |

### 10.6 Supplier Candidates

| Supplier | Resource | Available | ETA | Route Risk |
|---|---|---:|---:|---|
| MedSupply Oakland | Burn kits | 300 | 42m | Medium |
| UCSF Storage | Albuterol | 150 | 28m | Low |
| NorCal Oxygen | Oxygen cylinders | 80 | 91m | Low |
| Sacramento MedDepot | Burn kits | 900 | 138m | Medium |
| San Jose Warehouse | Oxygen cylinders | 120 | 104m | Low |

---

## 11. Agent 设计

### 11.1 Agent 角色

Agent 名称：CrisisFlow Dispatch Agent

Agent 职责：

- 接收灾害上下文。
- 预测医疗资源需求。
- 查询医院能力和库存。
- 计算资源缺口。
- 查询供应商网络。
- 对比调拨方案。
- 生成推荐计划。
- 创建审批请求。
- 生成简报和通知。

### 11.2 Agent 不允许做什么

Agent 不允许：

- 未经审批直接发出高风险调拨。
- 未经审批直接转院或改变医院分流策略。
- 忽略供应商合同状态。
- 忽略其他区域库存风险。
- 伪造真实数据来源。

### 11.3 Agent Tools

建议后端暴露以下工具函数：

#### get_incident_context(incident_id)

返回灾害事件、天气、风向、人口影响、道路风险。

#### estimate_patient_surge(incident_context)

根据灾害类型、人口、风向、历史规则，返回预计患者类型和数量。

#### get_hospital_capacity(region)

查询区域医院床位、ICU、烧伤科、呼吸床位、急诊压力。

#### get_medical_inventory(hospital_id)

查询医院药品和医疗物资库存。

#### calculate_resource_gap(patient_estimate, hospital_inventory, hospital_capacity)

计算需要、可用、缺口和短缺时间。

#### find_nearby_suppliers(resource_type, quantity_needed, destination)

查询预认证供应商、医院备用库存和仓库节点。

#### compare_eta_options(candidates, traffic_routes)

比较 ETA、路线风险、库存、合同状态。

#### rank_dispatch_plan(resource_gaps, supplier_options)

生成排序后的调拨方案。

#### create_approval_request(dispatch_plan)

为高风险动作生成审批请求。

#### send_emergency_dispatch_request(approval_id)

审批后向供应商、医院或物流方发送正式调拨请求。

#### generate_briefing(incident_id, dispatch_plan, audience)

生成不同受众的 briefing。

### 11.4 Agent 输出格式

Agent 输出建议统一成结构化 JSON，再由前端渲染。

示例：

```json
{
  "plan_id": "PLAN-2026-0529-014",
  "summary": "SF General will exceed burn and respiratory treatment capacity within 2.1 hours.",
  "recommendations": [
    {
      "action": "Transfer 300 burn kits from MedSupply Oakland to SF General",
      "resource": "Burn kits",
      "quantity": 300,
      "eta_min": 42,
      "why": "SF General has a 240-unit burn kit gap.",
      "risk_if_delayed": "Burn care shortage before second patient wave.",
      "approval_required": "Health Department",
      "confidence": "High"
    }
  ]
}
```

---

## 12. 调拨排序逻辑

Hackathon 版本可以使用简单规则，不需要复杂 ML。

### 12.1 推荐评分

每个供应选项计算 score：

```text
score =
  inventory_fit_score * 0.35
  + eta_score * 0.35
  + route_safety_score * 0.15
  + contract_score * 0.10
  + fallback_score * 0.05
```

### 12.2 规则说明

inventory_fit_score:

- 库存 >= 缺口：100
- 库存覆盖 50%-99%：70
- 库存覆盖 <50%：40

eta_score:

- ETA <= 45 min：100
- ETA 46-90 min：75
- ETA 91-150 min：50
- ETA >150 min：25

route_safety_score:

- Low risk：100
- Medium risk：70
- High risk：35
- Blocked：0

contract_score:

- Pre-approved：100
- Existing vendor：80
- Portal only：60
- Emergency contact only：40

fallback_score:

- API confirmed：100
- Portal confirmation：75
- Email/SMS fallback：50

### 12.3 输出结果

Agent 不只给一个结果，要给 top 3 options 和 backup。

示例：

- Best: MedSupply Oakland, ETA 42m, 300 burn kits.
- Backup: Sacramento MedDepot, ETA 138m, 900 burn kits.
- Partial backup: UCSF Storage, ETA 28m, 90 burn kits.

---

## 13. 系统架构

### 13.1 MVP 架构

Frontend:

- Next.js 或 React
- Dashboard UI
- Map mock view
- Agent panel
- Approval queue

Backend:

- FastAPI 或 Node.js
- Agent tool endpoints
- Mock data query logic
- Dispatch scoring logic
- Briefing generation API

AI:

- Gemini
- Google Cloud Agent Builder 或 ADK

Data:

- BigQuery
- Mock CSV / Google Sheets / Postgres source

MCP:

- Fivetran MCP

Hosting:

- Cloud Run

Optional:

- Arize Phoenix for agent tracing

### 13.2 数据流

```text
Hospital mock data
Supplier mock data
Traffic mock data
Incident mock data
        |
        v
Fivetran MCP / simulated Fivetran pipeline
        |
        v
BigQuery unified emergency data layer
        |
        v
Backend Agent Tools
        |
        v
Gemini Dispatch Agent
        |
        v
Resource gaps + Dispatch plan + Approval requests + Briefings
        |
        v
Command Center UI
```

### 13.3 Fivetran 在 Demo 中的解释

如果真正接入 Fivetran MCP 时间不够，也要在产品里清楚展示 integration layer。

推荐文案：

> CrisisFlow uses Fivetran as the data foundation for emergency AI. Hospital capacity, supplier inventory, logistics status, and incident feeds are synchronized into BigQuery, where the Gemini-powered agent can reason across all operational data in real time.

---

## 14. 供应商网络设计

### 14.1 平时平台要维护什么

每个城市提前维护：

- 预认证医院。
- 药品供应商。
- 医疗器械供应商。
- 区域仓库。
- 冷链和普通物流公司。
- 应急联系人。
- 备用联系人。
- 可供物资类别。
- 服务覆盖区域。
- SLA。
- 合同状态。
- 授权级别。
- 接入方式。

### 14.2 灾时 Agent 怎么找货

Agent 不应全网搜索，而应按优先级查询：

1. 当前医院库存。
2. 同城合作医院备用库存。
3. 预认证供应商库存。
4. 区域仓库。
5. 外部 backup supplier。
6. 紧急联系人 fallback。

### 14.3 发送调拨请求的三种方式

Level 1: API Integrated

供应商系统已接入，平台直接发送结构化请求，并接收确认。

Level 2: Supplier Portal

供应商没有 API，但可以登录 CrisisFlow Portal 确认请求。

Level 3: Emergency Contact Fallback

供应商没有系统接入，平台自动发送：

- Email
- SMS
- Voice call

注意：这些都应该由 CrisisFlow 平台发送，不能表现成 Agent 私下乱发。

---

## 15. Demo 视频脚本

总时长：3 分钟以内。

### 0:00 - 0:20 Problem

旁白：

> During a disaster, emergency teams do not lack data. They lack coordinated, real-time decisions across hospitals, suppliers, logistics teams, and government approvers.

画面：

- 山火背景。
- 数据源分散：hospital system, supplier inventory, traffic, weather, emergency contacts。

### 0:20 - 0:45 Incident Enters System

旁白：

> CrisisFlow receives a wildfire incident near Marin County. Winds are pushing smoke toward San Francisco, and Highway 101 is becoming congested.

画面：

- Command Center。
- Incident Summary Bar。
- 地图上火点、风向、医院。

### 0:45 - 1:15 Agent Checks Data

旁白：

> The Gemini-powered agent uses Fivetran-connected emergency data in BigQuery to check weather, hospital capacity, medical inventory, supplier stock, and route ETA.

画面：

- Agent Panel 工具调用状态。
- `Checking hospital capacity`
- `Finding nearby suppliers`
- `Ranking ETA options`

### 1:15 - 1:45 Resource Gap

旁白：

> CrisisFlow predicts 180 patients in the next 2.5 hours and identifies critical shortages in burn kits, albuterol, oxygen cylinders, ICU beds, and ER nurses.

画面：

- Resource Gap Table。
- 高亮缺口。

### 1:45 - 2:20 Dispatch Plan

旁白：

> The agent searches the pre-vetted emergency supplier network and recommends the fastest safe dispatch plan.

画面：

- MedSupply Oakland: 300 burn kits, ETA 42m。
- UCSF Storage: 150 albuterol, ETA 28m。
- NorCal Oxygen: 40 oxygen cylinders, ETA 91m。
- ETA comparison table。

### 2:20 - 2:45 Human Approval

旁白：

> CrisisFlow does not let AI execute life-critical actions alone. The agent creates approval-ready requests for the EOC and Health Department.

画面：

- Approval Queue。
- 点击 Approve Dispatch Plan。
- 状态变为 Approved。

### 2:45 - 3:00 Dispatch and Briefing

旁白：

> Once approved, CrisisFlow sends emergency dispatch requests through the platform and generates briefings for city leaders, hospitals, and suppliers.

画面：

- Dispatch Request Sent。
- Supplier Accepted。
- Generate Mayor Briefing。

结尾字幕：

> CrisisFlow AI: From incident alert to approved medical dispatch plan in 5 minutes.

---

## 16. Devpost / Pitch 文案

### 16.1 英文短描述

CrisisFlow AI is a Gemini-powered emergency medical supply chain agent for disaster response. When a wildfire or major incident occurs, it estimates patient surge and resource demand, checks hospital capacity and medical inventory, searches nearby hospitals and pre-vetted suppliers for available stock, compares ETA and route risk, then generates an approval-ready dispatch plan for emergency operations teams.

### 16.2 中文短描述

CrisisFlow AI 是一个面向灾害应急的医疗供应链调度 Agent。灾害发生后，它预测伤员规模和医疗资源需求，检查医院床位、药品和人力是否足够；若不足，则自动查询周边医院、供应商和仓储节点的可用资源，对比 ETA、路线风险和调拨成本，生成可审批的调度方案，帮助应急中心在关键几分钟内做出决策。

### 16.3 核心 tagline

From incident alert to approved medical dispatch plan in 5 minutes.

### 16.4 三句 pitch

1. Emergency teams do not lack data; they lack coordinated, real-time decisions.
2. CrisisFlow turns fragmented hospital, supplier, traffic, and incident data into an approved medical dispatch plan.
3. The AI recommends and explains; humans approve; the platform dispatches.

---

## 17. MVP 开发计划

### Day 1: 产品和数据

- 锁定 Marin wildfire demo。
- 建 mock data CSV / JSON。
- 定页面结构。
- 写资源缺口计算逻辑。

### Day 2: 前端主页面

- Command Center。
- Incident Drawer。
- Resource Gap 页面。
- Mock map。

### Day 3: Agent 和后端工具

- 实现 tool endpoints。
- 接 Gemini。
- 让 Agent 能调用工具并生成 plan。

### Day 4: Supplier Network 和 Dispatch Plan

- Supplier Network 页面。
- ETA ranking。
- Dispatch Plan 卡片。

### Day 5: Approval 和 Briefing

- Approval Queue。
- Dispatch Request 状态。
- Briefing Generator。
- Emergency Alert mock。

### Day 6: Cloud 和提交

- BigQuery 数据。
- Fivetran MCP 或 Fivetran integration story。
- Cloud Run 部署。
- 录 demo 视频。
- 写 Devpost。

---

## 18. MVP 范围控制

### 必须做

- 一个完整灾害故事。
- Command Center 页面。
- Resource Gap 分析。
- Supplier Network。
- Dispatch Plan。
- Approval Queue。
- Briefing Generator。
- Gemini Agent 工具调用。
- Fivetran/BigQuery 数据整合故事。

### 不要做

- 不做真实山火检测。
- 不做真实医院系统接入。
- 不做完整 GIS。
- 不做真实短信电话。
- 不做多灾种全覆盖。
- 不做复杂 ML 模型。
- 不做面向公众的大型网页。

---

## 19. 成功标准

Demo 成功的标准：

- 评委 10 秒内看懂这是应急医疗调度系统。
- 评委看到 Agent 查了多个数据源。
- 评委看到资源缺口不是编的一句话，而是结构化计算。
- 评委看到 Agent 比较了多个供应商和 ETA。
- 评委看到人类审批机制。
- 评委看到 Fivetran 与 Google Cloud 的合理使用。

---

## 20. 最终产品逻辑

最清晰的产品逻辑如下：

```text
Disaster happens
    |
    v
Agent estimates patient surge
    |
    v
Agent checks hospital capacity and inventory
    |
    v
Resource gaps detected
    |
    v
Agent searches pre-vetted city supplier network
    |
    v
Agent compares ETA, stock, route risk, contract status
    |
    v
Agent generates dispatch plan
    |
    v
Commander / EOC approves
    |
    v
CrisisFlow sends dispatch request
    |
    v
Supplier confirms
    |
    v
Agent monitors and replans if needed
```

一句话：

> CrisisFlow AI predicts what emergency medical resources will be missing, finds the nearest approved sources, ranks dispatch options by ETA and risk, and turns the result into an approved action plan.
