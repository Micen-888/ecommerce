// =========================================================
// MONGODB AGGREGATION PIPELINES
// Project: Global E-Commerce OLAP Dashboard
// =========================================================

// Problem 3: Combine discount data with shipping data by order_id
db.transaction_logs.aggregate([
  {
    $lookup: {
      from: "shipping_details",
      localField: "order_id",
      foreignField: "order_id",
      as: "shipping_detail"
    }
  },
  { $unwind: "$shipping_detail" },
  {
    $project: {
      _id: 0,
      order_id: 1,
      payment_method: "$payment.method",
      discount_percent: "$pricing.discount_percent",
      shipping_cost: "$shipping_detail.shipping.cost",
      region: "$shipping_detail.destination.region",
      country: "$shipping_detail.destination.country"
    }
  }
]);

// Distribution of payment method, retained as supporting insight only
db.transaction_logs.aggregate([
  {
    $group: {
      _id: "$payment.method",
      total_transactions: { $sum: 1 },
      avg_discount: { $avg: "$pricing.discount_percent" }
    }
  },
  { $sort: { total_transactions: -1 } }
]);
