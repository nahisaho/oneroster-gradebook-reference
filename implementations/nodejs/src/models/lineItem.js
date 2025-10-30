const { DataTypes } = require('sequelize');

module.exports = (sequelize) => {
  const LineItem = sequelize.define(
    'LineItem',
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
      description: {
        type: DataTypes.TEXT,
        allowNull: true,
      },
      assignDate: {
        type: DataTypes.DATE,
        allowNull: true,
        field: 'assign_date',
      },
      dueDate: {
        type: DataTypes.DATE,
        allowNull: true,
        field: 'due_date',
      },
      classSourcedId: {
        type: DataTypes.STRING(255),
        allowNull: false,
        field: 'class_sourced_id',
        validate: {
          notEmpty: true,
        },
      },
      categorySourcedId: {
        type: DataTypes.STRING(255),
        allowNull: true,
        field: 'category_sourced_id',
        references: {
          model: 'categories',
          key: 'sourced_id',
        },
        onDelete: 'SET NULL',
        onUpdate: 'CASCADE',
      },
      gradingPeriodSourcedId: {
        type: DataTypes.STRING(255),
        allowNull: true,
        field: 'grading_period_sourced_id',
      },
      resultValueMin: {
        type: DataTypes.DECIMAL(10, 2),
        allowNull: false,
        defaultValue: 0,
        field: 'result_value_min',
      },
      resultValueMax: {
        type: DataTypes.DECIMAL(10, 2),
        allowNull: false,
        field: 'result_value_max',
        validate: {
          isGreaterThanMin(value) {
            if (parseFloat(value) <= parseFloat(this.resultValueMin)) {
              throw new Error('resultValueMax must be greater than resultValueMin');
            }
          },
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
      tableName: 'line_items',
      timestamps: false,
      underscored: true,
      hooks: {
        beforeUpdate: (lineItem) => {
          lineItem.dateLastModified = new Date();
        },
        beforeValidate: (lineItem) => {
          // Validate due date is after assign date
          if (lineItem.assignDate && lineItem.dueDate) {
            if (new Date(lineItem.dueDate) <= new Date(lineItem.assignDate)) {
              throw new Error('dueDate must be after assignDate');
            }
          }
        },
      },
    }
  );

  // Instance methods
  LineItem.prototype.toJSON = function () {
    const values = { ...this.get() };
    
    // Convert to OneRoster format
    return {
      sourcedId: values.sourcedId,
      status: values.status,
      dateLastModified: values.dateLastModified.toISOString(),
      title: values.title,
      ...(values.description && { description: values.description }),
      ...(values.assignDate && { assignDate: values.assignDate.toISOString().split('T')[0] }),
      ...(values.dueDate && { dueDate: values.dueDate.toISOString().split('T')[0] }),
      class: {
        href: `${process.env.ROSTERING_SERVICE_BASE_URL}/classes/${values.classSourcedId}`,
        sourcedId: values.classSourcedId,
        type: 'class',
      },
      ...(values.categorySourcedId && {
        category: {
          href: `${process.env.API_BASE_URL}/categories/${values.categorySourcedId}`,
          sourcedId: values.categorySourcedId,
          type: 'category',
        },
      }),
      ...(values.gradingPeriodSourcedId && {
        gradingPeriod: {
          href: `${process.env.ROSTERING_SERVICE_BASE_URL}/academicSessions/${values.gradingPeriodSourcedId}`,
          sourcedId: values.gradingPeriodSourcedId,
          type: 'academicSession',
        },
      }),
      resultValueMin: parseFloat(values.resultValueMin),
      resultValueMax: parseFloat(values.resultValueMax),
      ...(values.metadata && { metadata: values.metadata }),
    };
  };

  // Class methods
  LineItem.associate = (models) => {
    LineItem.belongsTo(models.Category, {
      foreignKey: 'categorySourcedId',
      as: 'category',
    });
    LineItem.hasMany(models.Result, {
      foreignKey: 'lineItemSourcedId',
      as: 'results',
    });
  };

  return LineItem;
};
