export const steps = [
  { id: "home", label: "Trending Topics" },
  { id: "match", label: "Course Match" },
  { id: "summary", label: "AI Summary" },
  { id: "programme", label: "Programme" },
  { id: "personalized", label: "Personalized Learning" },
  { id: "teacher", label: "Teacher" },
  { id: "marketing", label: "Marketing" },
  { id: "income", label: "Income" },
];

export function computeFinance(students, price, costs) {
  const revenue = students * price;
  const profit = revenue - costs;

  return {
    revenue,
    profit,
    breakEvenPrice: students > 0 ? costs / students : 0,
    breakEvenStudents: price > 0 ? Math.ceil(costs / price) : 0,
  };
}
