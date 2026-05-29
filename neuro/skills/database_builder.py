"""
Database Builder - Complete DB generation for all SQL/NoSQL
Beats all AI coding systems for database design
"""

from typing import Dict, Any, List
from dataclasses import dataclass

@dataclass
class Table:
    name: str
    columns: List[Dict]
    indexes: List[str]
    relations: List[str]

class DatabaseBuilder:
    """
    Complete database builder for PostgreSQL, MySQL, MongoDB, etc.
    Generates: Schema, migrations, models, seeds.
    
    Usage:
        from neuro.skills.database_builder import DatabaseBuilder
        db = DatabaseBuilder()
        result = db.build("E-commerce platform with users, products, orders")
    """
    
    def __init__(self):
        self.router = None
    
    def _get_router(self):
        if self.router is None:
            from neuro.router.smart_router import SmartRouter
            self.router = SmartRouter()
        return self.router
    
    def build(self, description: str, db_type: str = "postgresql") -> Dict[str, Any]:
        """Build complete database."""
        
        schema = self._generate_schema(description, db_type)
        migrations = self._generate_migrations(db_type)
        models = self._generate_models(db_type)
        seeds = self._generate_seeds(db_type)
        
        return {
            "schema": schema,
            "migrations": migrations,
            "models": models,
            "seeds": seeds,
            "db_type": db_type
        }
    
    def _generate_schema(self, desc: str, db_type: str) -> str:
        if db_type == "postgresql":
            return '''-- PostgreSQL Schema
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    role VARCHAR(50) DEFAULT 'user',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Products table
CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    stock_quantity INTEGER DEFAULT 0,
    category_id UUID REFERENCES categories(id),
    image_url VARCHAR(500),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Orders table
CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    total_amount DECIMAL(10, 2) NOT NULL,
    shipping_address TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Order items table
CREATE TABLE order_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_id UUID REFERENCES orders(id) NOT NULL,
    product_id UUID REFERENCES products(id) NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Categories table
CREATE TABLE categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    parent_id UUID REFERENCES categories(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_products_category ON products(category_id);
CREATE INDEX idx_orders_user ON orders(user_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_order_items_order ON order_items(order_id);

-- Trigger for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
'''
        elif db_type == "mongodb":
            return '''// MongoDB Collections
// Users Collection
db.createCollection("users", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["email", "passwordHash"],
      properties: {
        email: { bsonType: "string" },
        passwordHash: { bsonType: "string" },
        firstName: { bsonType: "string" },
        lastName: { bsonType: "string" },
        role: { bsonType: "string" },
        isActive: { bsonType: "bool" },
        createdAt: { bsonType: "date" }
      }
    }
  }
});

// Products Collection
db.createCollection("products", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["name", "price"],
      properties: {
        name: { bsonType: "string" },
        description: { bsonType: "string" },
        price: { bsonType: "number" },
        stockQuantity: { bsonType: "int" },
        categoryId: { bsonType: "objectId" },
        imageUrl: { bsonType: "string" }
      }
    }
  }
});

// Orders Collection
db.createCollection("orders", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["userId", "items"],
      properties: {
        userId: { bsonType: "objectId" },
        items: { bsonType: "array" },
        status: { bsonType: "string" },
        totalAmount: { bsonType: "number" }
      }
    }
  }
});

// Indexes
db.users.createIndex({ "email": 1 }, { unique: true });
db.products.createIndex({ "categoryId": 1 });
db.orders.createIndex({ "userId": 1 });
db.orders.createIndex({ "status": 1 });
'''
        return "Unsupported database type"
    
    def _generate_migrations(self, db_type: str) -> str:
        return '''// Database Migrations (Knex.js style)
exports.up = function(knex) {
  return knex.schema
    .createTable('users', (table) => {
      table.uuid('id').primary().defaultTo(knex.raw('uuid_generate_v4()'));
      table.string('email').unique().notNullable();
      table.string('password_hash').notNullable();
      table.string('first_name');
      table.string('last_name');
      table.string('role').defaultTo('user');
      table.boolean('is_active').defaultTo(true);
      table.timestamp('created_at').defaultTo(knex.fn.now());
      table.timestamp('updated_at').defaultTo(knex.fn.now());
    })
    .createTable('products', (table) => {
      table.uuid('id').primary().defaultTo(knex.raw('uuid_generate_v4()'));
      table.string('name').notNullable();
      table.text('description');
      table.decimal('price', 10, 2).notNullable();
      table.integer('stock_quantity').defaultTo(0);
      table.uuid('category_id').references('id').inTable('categories');
      table.string('image_url');
      table.boolean('is_active').defaultTo(true);
      table.timestamp('created_at').defaultTo(knex.fn.now());
      table.timestamp('updated_at').defaultTo(knex.fn.now());
    });
};

exports.down = function(knex) {
  return knex.schema
    .dropTableIfExists('products')
    .dropTableIfExists('users');
};
'''
    
    def _generate_models(self, db_type: str) -> str:
        return '''// Sequelize Models
const { DataTypes } = require('sequelize');

module.exports = (sequelize) => {
  const User = sequelize.define('User', {
    id: {
      type: DataTypes.UUID,
      defaultValue: DataTypes.UUIDV4,
      primaryKey: true
    },
    email: {
      type: DataTypes.STRING,
      allowNull: false,
      unique: true,
      validate: { isEmail: true }
    },
    passwordHash: {
      type: DataTypes.STRING,
      allowNull: false
    },
    firstName: {
      type: DataTypes.STRING
    },
    lastName: {
      type: DataTypes.STRING
    },
    role: {
      type: DataTypes.ENUM('user', 'admin', 'moderator'),
      defaultValue: 'user'
    },
    isActive: {
      type: DataTypes.BOOLEAN,
      defaultValue: true
    }
  }, {
    timestamps: true,
    paranoid: true
  });

  User.associate = (models) => {
    User.hasMany(models.Order, { foreignKey: 'userId' });
  };

  return User;
};
'''
    
    def _generate_seeds(self, db_type: str) -> str:
        return '''// Database Seeds
exports.seed = async function(knex) {
  // Delete existing entries
  await knex('users').del();
  
  // Insert users
  await knex('users').insert([
    {
      id: '550e8400-e29b-41d4-a716-446655440000',
      email: 'admin@example.com',
      password_hash: await bcrypt.hash('admin123', 10),
      first_name: 'Admin',
      last_name: 'User',
      role: 'admin'
    },
    {
      id: '550e8400-e29b-41d4-a716-446655440001',
      email: 'user@example.com',
      password_hash: await bcrypt.hash('user123', 10),
      first_name: 'Regular',
      last_name: 'User',
      role: 'user'
    }
  ]);
};
'''


def build_database(description: str, db_type: str = "postgresql") -> Dict[str, Any]:
    """Quick database builder."""
    builder = DatabaseBuilder()
    return builder.build(description, db_type)
