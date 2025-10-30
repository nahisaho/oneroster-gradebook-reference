const { DataTypes } = require('sequelize');

module.exports = (sequelize) => {
  const Result = sequelize.define(
    'Result',
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
      lineItemSourcedId: {
        type: DataTypes.STRING(255),
        allowNull: false,
        field: 'line_item_sourced_id',
        references: {
          model: 'line_items',
          key: 'sourced_id',
        },
        onDelete: 'CASCADE',
        onUpdate: 'CASCADE',
      },
      studentSourcedId: {
        type: DataTypes.STRING(255),
        allowNull: false,
        field: 'student_sourced_id',
        validate: {
          notEmpty: true,
        },
      },
      scoreStatus: {
        type: DataTypes.ENUM('exempt', 'fully graded', 'not submitted', 'partially graded', 'submitted'),
        allowNull: false,
        field: 'score_status',
        validate: {
          isIn: [['exempt', 'fully graded', 'not submitted', 'partially graded', 'submitted']],
        },
      },
      score: {
        type: DataTypes.DECIMAL(10, 2),
        allowNull: true,
        validate: {
          isValidScore() {
            // Score is required for 'fully graded' and 'partially graded'
            const requireScore = ['fully graded', 'partially graded'];
            if (requireScore.includes(this.scoreStatus) && this.score === null) {
              throw new Error(`score is required when scoreStatus is '${this.scoreStatus}'`);
            }
            // Score should be null for 'exempt' and 'not submitted'
            const noScore = ['exempt', 'not submitted'];
            if (noScore.includes(this.scoreStatus) && this.score !== null) {
              throw new Error(`score must be null when scoreStatus is '${this.scoreStatus}'`);
            }
          },
        },
      },
      scoreDate: {
        type: DataTypes.DATE,
        allowNull: true,
        field: 'score_date',
      },
      comment: {
        type: DataTypes.TEXT,
        allowNull: true,
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
      tableName: 'results',
      timestamps: false,
      underscored: true,
      indexes: [
        {
          unique: true,
          fields: ['line_item_sourced_id', 'student_sourced_id'],
          name: 'idx_results_lineitem_student',
        },
        {
          fields: ['student_sourced_id'],
          name: 'idx_results_student',
        },
        {
          fields: ['score_status'],
          name: 'idx_results_score_status',
        },
        {
          fields: ['date_last_modified'],
          name: 'idx_results_date_last_modified',
        },
      ],
      hooks: {
        beforeUpdate: (result) => {
          result.dateLastModified = new Date();
        },
        beforeValidate: async (result, options) => {
          // Validate score is within lineItem's min/max range
          if (result.score !== null) {
            const LineItem = sequelize.models.LineItem;
            const lineItem = await LineItem.findByPk(result.lineItemSourcedId);
            
            if (lineItem) {
              const score = parseFloat(result.score);
              const min = parseFloat(lineItem.resultValueMin);
              const max = parseFloat(lineItem.resultValueMax);
              
              if (score < min || score > max) {
                throw new Error(
                  `score must be between ${min} and ${max} for this lineItem`
                );
              }
            }
          }
        },
      },
    }
  );

  // Instance methods
  Result.prototype.toJSON = function () {
    const values = { ...this.get() };
    
    // Convert to OneRoster format
    return {
      sourcedId: values.sourcedId,
      status: values.status,
      dateLastModified: values.dateLastModified.toISOString(),
      lineItem: {
        href: `${process.env.API_BASE_URL}/lineItems/${values.lineItemSourcedId}`,
        sourcedId: values.lineItemSourcedId,
        type: 'lineItem',
      },
      student: {
        href: `${process.env.ROSTERING_SERVICE_BASE_URL}/users/${values.studentSourcedId}`,
        sourcedId: values.studentSourcedId,
        type: 'user',
      },
      scoreStatus: values.scoreStatus,
      ...(values.score !== null && values.score !== undefined && { score: parseFloat(values.score) }),
      ...(values.scoreDate && { scoreDate: values.scoreDate.toISOString() }),
      ...(values.comment && { comment: values.comment }),
      ...(values.metadata && { metadata: values.metadata }),
    };
  };

  // Class methods
  Result.associate = (models) => {
    Result.belongsTo(models.LineItem, {
      foreignKey: 'lineItemSourcedId',
      as: 'lineItem',
    });
  };

  return Result;
};
