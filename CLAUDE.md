# CLAUDE.md
该文件提供了在该存储库中使用代码时对Claude Code（Claude.ai/Code）的指导。

## 项目概况
Lorelm是一个基于FastAPI的应用程序，支持PostgreSQL数据库，具有LLM集成和RAG功能。该项目遵循一个干净的架构，具有明确的关注点分离。

## 辅助编程
### 要求
注释、文档、回答始终使用简体中文进行编写和回复

## 通用开发命令
### 后端开发
```bash
# Start PostgreSQL via Docker
docker-compose up -d

# Create new migration
uv run alembic revision --autogenerate -m "description"

# Check database status
uv run alembic current
```

### 数据库
```bash
# Start PostgreSQL via Docker
docker-compose up -d

# Create new migration
uv run alembic revision --autogenerate -m "description"

# Check database status
uv run alembic current
```

## 架构（Architecture）
### 核心结构

- **后端**:FastAPI应用程序位于`backend/`目录中
- **前端**:Vue 3 + Vite应用程序位于`frontend/`目录中
- **数据库**:PostgreSQL，具有用于向量操作的pgvector扩展
- **ORM**：具有异步支持的SQLAlchemy，对公共字段使用自定义基类
- **API**：RESTful API，在`backend/api/v1`下

### API层

- **Schemas**：位于Pydantic模型的`backend/Schemas/`目录中
- **响应模型**：不同模块的单独文件（`admin.py`、`character.py`和`conversation.py`）
- **通用模式**：通用响应的基本架构（`PageResponse`、`ORMBase`等）

### 关键组成部分
#### 数据库层

- **Models**：位于`backend/Models/`中，基类在`backend/Models/base.py中`
- **CRUD**：`backend/CRUD/`目录中的数据库操作
- **基类**：
- `DbBase`：SQLAlchemy声明基
- `TableBase`：带ID字段的基
- `ORMBaseSmall`：具有created_at时间戳的基数
- `ORMBase`：带updated_at、deleted_at和is_delete字段的完整基数

#### 数据库模型

-**Admin**：用户管理（`User`）
-**字符**：角色扮演系统的字符、世界、标签、文档模型
-**对话**:LLM对话会话和消息模型（`ConversationSession`，`ConversionHistory`，`Session2Character`）

#### 应用程序工厂

-**主应用程序**：`backend/__init__.py`包含`create_App（）`函数
-**生命周期**：通过异步上下文管理器处理数据库初始化/取消初始化
-**中间件**：通过`make_middlewares（）`函数应用

#### 依赖关系

-**数据库**：通过`get_session（）`context manager进行异步会话管理
-**配置**：从`.env`文件加载的环境变量

### 数据库配置

- 将PostgreSQL与pgvector扩展一起用于向量嵌入
- 具有异步驱动程序的异步SQLAlchemy
- 具有`is_delete`和`deleted_at`字段的软删除模式
- 通过SQLAlchemy触发器自动管理时间戳
### LLM集成

- 用于大型语言模型功能的Modelscope集成
- 通过pgvector支持向量搜索
- 格式错误的LLM响应的JSON修复功能

## 前端迁移
### Schemas
1. 理解`backend/schemas`中的数据结构和继承关系
2. 在`backend/schemas`中创建对应种类文件夹（假设是`admin`）
   1. 创建文件夹`backend/schemas/admin`，创建接口文件`frontend/src/schemas/admin/index.ts`，创建枚举文件`frontend/src/schemas/admin/types.ts`
   2. 将`backend/schemas/admin.py`中的内容的响应体，以ts的interface格式保存在`frontend/src/schemas/admin/index.ts`中
   3. 将`backend/schemas/admin.py`中的枚举定义，以ts的enum格式保存在`frontend/src/schemas/admin/types.ts`中
3. 检查创建的接口是否齐全，注释是否完善，继承关系是否正确

#### 枚举示例

```typescript
export const DataRange = {
  /** 全部数据权限 */
  ALL: "all",
  /** 仅自身数据 */
  SELF: "self",
  /** 部门数据权限 */
  DEPARTMENT: "dept",
  /** 部门及子部门数据 */
  DEPARTMENT_AND_CHILDREN: "dept_and_children",
  /** 自定义数据权限 */
  CUSTOM: "custom",
}
export type DataRange = typeof DataRange[keyof typeof DataRange];
```


## 项目设置
1. 将`.env.example`复制到`.env`并配置数据库设置
2. 运行“uv sync”以安装依赖项
3. 启动PostgreSQL:`docker compose up-d`
4. 运行迁移：`uv Run alembic upgrade head`
5. 启动开发服务器：`uv run uvicorn backend:app--reload`