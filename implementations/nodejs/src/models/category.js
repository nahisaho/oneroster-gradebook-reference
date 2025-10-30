const { DataTypes } = require('sequelize');

module.exports = (sequelize) => {
  const Category = sequelize.define(
    'Category',
    {
      sourcedId: {
        type: DataTypes.STRING(255),
        primaryKey: true,
        field: 'sourced_id',
        allowNull: false,
      },
      status: {
        type: DataTypes.ENUM('active', 'tobedeleted'),
        allowNull: false,
        defaultValue: 'active',
        validate: {
          isIn: [['active', 'tobedeleted']],
        },
      },
      dateLastModified: {
        type: DataTypes.DATE,
        allowNull: false,
        defaultValue: DataTypes.NOW,
        field: 'date_last_modified',
      },
      title: {
        type: DataTypes.STRING(255),
        allowNull: false,
        validate: {
          notEmpty: true,
          len: [1, 255],
        },
      },
      weight: {
        type: DataTypes.DECIMAL(5, 4),
        allowNull: true,
        validate: {
          min: 0.0,
          max: 1.0,
        },
      },
      metadata: {
        type: DataTypes.JSONB,
        allowNull: true,
      },
      createdAt: {
        type: DataTypes.DATE,
        allowNull: false,
        defaultValue: DataTypes.NOW,
        field: 'created_at',
      },
    },
    {
      tableName: 'categories',
      timestamps: false,
      underscored: true,
      hooks: {
        beforeUpdate: (category) => {
          category.dateLastModified = new Date();
        },
      },
    }
  );

  // Instance methods
  Category.prototype.toJSON = function () {
    const values = { ...this.get() };
    
    // Convert to OneRoster format
    return {
      sourcedId: values.sourcedId,
      status: values.status,
      dateLastModified: values.dateLastModified.toISOString(),
      title: values.title,
      ...(values.weight !== null && { weight: parseFloat(values.weight) }),
      ...(values.metadata && { metadata: values.metadata }),
    };
  };

  // Class methods
  Category.associate = (models) => {
    Category.hasMany(models.LineItem, {
      foreignKey: 'categorySourcedId',
      as: 'lineItems',
    });
  };

  return Category;
};
