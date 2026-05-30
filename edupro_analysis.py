import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import warnings
import os

warnings.filterwarnings("ignore")

os.makedirs("edupro_charts", exist_ok=True)

PALETTE  = "Set2"
FIG_SIZE = (10, 6)


FILE = "EduPro_Online_Platform.xlsx"

users        = pd.read_excel(FILE, sheet_name="Users")
courses      = pd.read_excel(FILE, sheet_name="Courses")
transactions = pd.read_excel(FILE, sheet_name="Transactions")

for name, df in [("Users", users), ("Courses", courses), ("Transactions", transactions)]:
    print(f"{name}: {df.shape[0]:,} rows × {df.shape[1]} columns")



    users.drop_duplicates(subset="UserID", keep="first", inplace=True)
users.dropna(subset=["Age", "Gender"], inplace=True)
users["Age"] = users["Age"].astype(int)

def age_band(age):
    if age < 18:
        return "<18"
    elif age <= 25:
        return "18–25"
    elif age <= 35:
        return "26–35"
    elif age <= 45:
        return "36–45"
    else:
        return "45+"

AGE_ORDER = ["<18", "18–25", "26–35", "36–45", "45+"]
users["AgeBand"] = users["Age"].apply(age_band)
users["AgeBand"] = pd.Categorical(users["AgeBand"], categories=AGE_ORDER, ordered=True)

transactions.drop_duplicates(subset="TransactionID", keep="first", inplace=True)
transactions.dropna(subset=["UserID", "CourseID"], inplace=True)
transactions["TransactionDate"] = pd.to_datetime(transactions["TransactionDate"])
transactions["Year"]  = transactions["TransactionDate"].dt.year
transactions["Month"] = transactions["TransactionDate"].dt.to_period("M").astype(str)

courses.drop_duplicates(subset="CourseID", keep="first", inplace=True)

print("Users after cleaning   :", len(users))
print("Transactions cleaned   :", len(transactions))
print("Courses                :", len(courses))
print("Date range             :", transactions["TransactionDate"].min().date(),
      "→", transactions["TransactionDate"].max().date())


merged = transactions.merge(users, on="UserID", how="inner")
merged = merged.merge(courses, on="CourseID", how="inner")

print("Merged shape :", merged.shape)
print("Columns      :", list(merged.columns))


fig, ax = plt.subplots(figsize=FIG_SIZE)
ax.hist(users["Age"], bins=range(10, 55, 2), color="#4e79a7", edgecolor="white", linewidth=0.6)
ax.set_title("Age Distribution of EduPro Learners", fontsize=14, fontweight="bold")
ax.set_xlabel("Age")
ax.set_ylabel("Number of Learners")
ax.xaxis.set_major_locator(mticker.MultipleLocator(5))
plt.tight_layout()
plt.savefig("edupro_charts/01_age_distribution.png", dpi=150)
plt.show()

age_band_counts = users["AgeBand"].value_counts().reindex(AGE_ORDER)

fig, ax = plt.subplots(figsize=FIG_SIZE)
bars = ax.bar(age_band_counts.index, age_band_counts.values,
              color=sns.color_palette(PALETTE, len(AGE_ORDER)), edgecolor="white")
for bar in bars:
    ax.text(bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 10, f"{int(bar.get_height()):,}",
            ha="center", va="bottom", fontsize=9)
ax.set_title("Learners by Age Band", fontsize=14, fontweight="bold")
ax.set_xlabel("Age Group")
ax.set_ylabel("Number of Learners")
plt.tight_layout()
plt.savefig("edupro_charts/02_learners_by_age_band.png", dpi=150)
plt.show()

gender_counts = users["Gender"].value_counts()

fig, axes = plt.subplots(1, 2, figsize=(12, 5))
axes[0].pie(gender_counts, labels=gender_counts.index, autopct="%1.1f%%",
            colors=sns.color_palette(PALETTE, len(gender_counts)),
            startangle=90, wedgeprops={"edgecolor": "white", "linewidth": 1.5})
axes[0].set_title("Gender Distribution (Pie)", fontweight="bold")
axes[1].bar(gender_counts.index, gender_counts.values,
            color=sns.color_palette(PALETTE, len(gender_counts)), edgecolor="white")
for i, v in enumerate(gender_counts.values):
    axes[1].text(i, v + 5, f"{v:,}", ha="center", fontsize=10)
axes[1].set_title("Gender Distribution (Bar)", fontweight="bold")
axes[1].set_ylabel("Count")
plt.suptitle("EduPro Learner Gender Distribution", fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig("edupro_charts/03_gender_distribution.png", dpi=150, bbox_inches="tight")
plt.show()

print("Age-Band breakdown:\n", age_band_counts.to_string())
print("\nGender breakdown:\n", gender_counts.to_string())



cat_enroll = (merged.groupby("CourseCategory")["TransactionID"]
              .count()
              .sort_values(ascending=False)
              .reset_index(name="Enrollments"))

fig, ax = plt.subplots(figsize=(12, 6))
sns.barplot(data=cat_enroll, x="Enrollments", y="CourseCategory",
            palette=PALETTE, ax=ax, edgecolor="white")
for i, row in cat_enroll.iterrows():
    ax.text(row["Enrollments"] + 20, i, f"{row['Enrollments']:,}", va="center", fontsize=9)
ax.set_title("Total Enrollments by Course Category", fontsize=14, fontweight="bold")
ax.set_xlabel("Number of Enrollments")
ax.set_ylabel("Course Category")
plt.tight_layout()
plt.savefig("edupro_charts/04_enrollments_by_category.png", dpi=150)
plt.show()

type_enroll = merged["CourseType"].value_counts()

fig, ax = plt.subplots(figsize=(7, 5))
ax.pie(type_enroll, labels=type_enroll.index, autopct="%1.1f%%",
       colors=["#59a14f", "#e15759"], startangle=90,
       wedgeprops={"edgecolor": "white", "linewidth": 2})
ax.set_title("Enrollments: Free vs Paid Courses", fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig("edupro_charts/05_free_vs_paid.png", dpi=150)
plt.show()

level_order  = ["Beginner", "Intermediate", "Advanced"]
level_enroll = merged["CourseLevel"].value_counts().reindex(level_order, fill_value=0)

fig, ax = plt.subplots(figsize=(8, 5))
bars = ax.bar(level_enroll.index, level_enroll.values,
              color=["#76b7b2", "#f28e2b", "#e15759"], edgecolor="white")
for bar in bars:
    ax.text(bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 30, f"{int(bar.get_height()):,}",
            ha="center", fontsize=10, fontweight="bold")
ax.set_title("Enrollments by Course Level", fontsize=14, fontweight="bold")
ax.set_xlabel("Course Level")
ax.set_ylabel("Number of Enrollments")
plt.tight_layout()
plt.savefig("edupro_charts/06_enrollments_by_level.png", dpi=150)
plt.show()



age_enroll = (merged.groupby("AgeBand")["TransactionID"]
              .count()
              .reindex(AGE_ORDER, fill_value=0)
              .reset_index(name="Enrollments"))

fig, ax = plt.subplots(figsize=FIG_SIZE)
sns.barplot(data=age_enroll, x="AgeBand", y="Enrollments",
            palette=PALETTE, ax=ax, edgecolor="white")
for i, row in age_enroll.iterrows():
    ax.text(i, row["Enrollments"] + 15, f"{row['Enrollments']:,}",
            ha="center", fontsize=9, fontweight="bold")
ax.set_title("Enrollments by Age Band", fontsize=14, fontweight="bold")
ax.set_xlabel("Age Group")
ax.set_ylabel("Number of Enrollments")
plt.tight_layout()
plt.savefig("edupro_charts/07_enrollments_by_age_band.png", dpi=150)
plt.show()

heat_age_cat = (merged.pivot_table(index="AgeBand", columns="CourseCategory",
                                   values="TransactionID", aggfunc="count", fill_value=0)
                .reindex(AGE_ORDER).fillna(0).astype(int))

fig, ax = plt.subplots(figsize=(14, 6))
sns.heatmap(heat_age_cat, annot=True, fmt="d", cmap="YlOrRd",
            linewidths=0.5, linecolor="white", ax=ax, cbar_kws={"label": "Enrollments"})
ax.set_title("Heatmap: Age Band × Course Category", fontsize=14, fontweight="bold")
ax.set_xlabel("Course Category")
ax.set_ylabel("Age Group")
plt.xticks(rotation=30, ha="right")
plt.tight_layout()
plt.savefig("edupro_charts/08_heatmap_age_category.png", dpi=150)
plt.show()

heat_age_lvl = (merged.pivot_table(index="AgeBand", columns="CourseLevel",
                                   values="TransactionID", aggfunc="count", fill_value=0)
                .reindex(AGE_ORDER).fillna(0)[level_order].astype(int))

fig, ax = plt.subplots(figsize=(9, 5))
sns.heatmap(heat_age_lvl, annot=True, fmt="d", cmap="Blues",
            linewidths=0.5, linecolor="white", ax=ax, cbar_kws={"label": "Enrollments"})
ax.set_title("Heatmap: Age Band × Course Level", fontsize=14, fontweight="bold")
ax.set_xlabel("Course Level")
ax.set_ylabel("Age Group")
plt.tight_layout()
plt.savefig("edupro_charts/09_heatmap_age_level.png", dpi=150)
plt.show()

gender_cat = (merged.groupby(["Gender", "CourseCategory"])["TransactionID"]
              .count().unstack(fill_value=0))

fig, ax = plt.subplots(figsize=(13, 6))
gender_cat.T.plot(kind="bar", ax=ax, colormap=PALETTE, edgecolor="white", width=0.7)
ax.set_title("Enrollments by Gender × Course Category", fontsize=14, fontweight="bold")
ax.set_xlabel("Course Category")
ax.set_ylabel("Enrollments")
ax.legend(title="Gender", bbox_to_anchor=(1, 1))
plt.xticks(rotation=30, ha="right")
plt.tight_layout()
plt.savefig("edupro_charts/10_gender_category.png", dpi=150, bbox_inches="tight")
plt.show()

gender_lvl = (merged.groupby(["Gender", "CourseLevel"])["TransactionID"]
              .count().unstack(fill_value=0)[level_order])

fig, ax = plt.subplots(figsize=(9, 5))
gender_lvl.plot(kind="bar", ax=ax, colormap=PALETTE, edgecolor="white", width=0.6)
ax.set_title("Enrollments by Gender × Course Level", fontsize=14, fontweight="bold")
ax.set_xlabel("Gender")
ax.set_ylabel("Enrollments")
ax.legend(title="Level")
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig("edupro_charts/11_gender_level.png", dpi=150)
plt.show()

gender_type = (merged.groupby(["Gender", "CourseType"])["TransactionID"]
               .count().unstack(fill_value=0))

fig, ax = plt.subplots(figsize=(8, 5))
gender_type.plot(kind="bar", ax=ax, color=["#59a14f", "#e15759"], edgecolor="white", width=0.5)
ax.set_title("Free vs Paid Course Preference by Gender", fontsize=14, fontweight="bold")
ax.set_xlabel("Gender")
ax.set_ylabel("Enrollments")
ax.legend(title="Course Type")
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig("edupro_charts/12_gender_free_vs_paid.png", dpi=150)
plt.show()



courses_per_user = (merged.groupby("UserID")["CourseID"]
                    .nunique()
                    .reset_index(name="CoursesEnrolled"))

avg_courses = courses_per_user["CoursesEnrolled"].mean()
print(f"Average courses per learner: {avg_courses:.2f}")

fig, ax = plt.subplots(figsize=FIG_SIZE)
ax.hist(courses_per_user["CoursesEnrolled"], bins=range(1, 16),
        color="#4e79a7", edgecolor="white", linewidth=0.6)
ax.axvline(avg_courses, color="red", linestyle="--", linewidth=2,
           label=f"Mean = {avg_courses:.1f}")
ax.set_title("Distribution of Courses Enrolled per Learner", fontsize=14, fontweight="bold")
ax.set_xlabel("Number of Courses")
ax.set_ylabel("Number of Learners")
ax.legend()
plt.tight_layout()
plt.savefig("edupro_charts/13_courses_per_learner.png", dpi=150)
plt.show()

top_courses = (merged.groupby("CourseName")["TransactionID"]
               .count()
               .sort_values(ascending=False)
               .head(10)
               .reset_index(name="Enrollments"))

fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(data=top_courses, x="Enrollments", y="CourseName",
            palette="Blues_d", ax=ax, edgecolor="white")
ax.set_title("Top 10 Most Enrolled Courses", fontsize=14, fontweight="bold")
ax.set_xlabel("Enrollments")
ax.set_ylabel("Course Name")
plt.tight_layout()
plt.savefig("edupro_charts/14_top10_courses.png", dpi=150)
plt.show()

monthly = (merged.groupby("Month")["TransactionID"]
           .count()
           .reset_index(name="Enrollments"))
monthly.sort_values("Month", inplace=True)

fig, ax = plt.subplots(figsize=(14, 5))
ax.plot(monthly["Month"], monthly["Enrollments"],
        marker="o", color="#4e79a7", linewidth=2, markersize=4)
ax.fill_between(monthly["Month"], monthly["Enrollments"], alpha=0.1, color="#4e79a7")
ax.set_title("Monthly Enrollment Trend", fontsize=14, fontweight="bold")
ax.set_xlabel("Month")
ax.set_ylabel("Enrollments")
step = max(1, len(monthly) // 12)
ax.set_xticks(range(0, len(monthly), step))
ax.set_xticklabels(monthly["Month"].iloc[::step], rotation=45, ha="right")
plt.tight_layout()
plt.savefig("edupro_charts/15_monthly_trend.png", dpi=150)
plt.show()

beg_adv = merged[merged["CourseLevel"].isin(["Beginner", "Advanced"])]
beg_adv_grp = (beg_adv.groupby(["AgeBand", "CourseLevel"])["TransactionID"]
               .count()
               .unstack(fill_value=0)
               .reindex(AGE_ORDER))

fig, ax = plt.subplots(figsize=(10, 5))
beg_adv_grp.plot(kind="bar", ax=ax, color=["#76b7b2", "#e15759"],
                 edgecolor="white", width=0.65)
ax.set_title("Beginner vs Advanced Enrollments by Age Band", fontsize=14, fontweight="bold")
ax.set_xlabel("Age Group")
ax.set_ylabel("Enrollments")
ax.legend(title="Level")
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig("edupro_charts/16_beginner_vs_advanced_age.png", dpi=150)
plt.show()


total_enrollments     = len(merged)
total_unique_learners = merged["UserID"].nunique()
total_courses         = merged["CourseID"].nunique()
most_popular_category = cat_enroll.iloc[0]["CourseCategory"]
most_popular_level    = level_enroll.idxmax()
gender_ratio          = gender_counts / gender_counts.sum() * 100
top_age_band          = age_enroll.sort_values("Enrollments", ascending=False).iloc[0]["AgeBand"]

print(f"Total Enrollments       : {total_enrollments:,}")
print(f"Unique Active Learners  : {total_unique_learners:,}")
print(f"Unique Courses          : {total_courses:,}")
print(f"Avg Courses / Learner   : {avg_courses:.2f}")
print(f"Most Popular Category   : {most_popular_category}")
print(f"Most Popular Level      : {most_popular_level}")
print(f"Most Active Age Band    : {top_age_band}")
for gender, pct in gender_ratio.items():
    print(f"{gender} Participation     : {pct:.1f}%")

kpi_labels = [
    f"Total Enrollments\n{total_enrollments:,}",
    f"Active Learners\n{total_unique_learners:,}",
    f"Avg Courses/Learner\n{avg_courses:.1f}",
    f"Top Category\n{most_popular_category}",
    f"Top Level\n{most_popular_level}",
    f"Top Age Band\n{top_age_band}",
]
colors = ["#4e79a7", "#f28e2b", "#59a14f", "#76b7b2", "#e15759", "#af7aa1"]

fig, axes = plt.subplots(1, 6, figsize=(18, 3))
fig.patch.set_facecolor("#f7f7f7")
for ax, label, color in zip(axes, kpi_labels, colors):
    ax.set_facecolor(color)
    ax.text(0.5, 0.5, label, transform=ax.transAxes,
            ha="center", va="center", fontsize=12, fontweight="bold",
            color="white", multialignment="center")
    ax.axis("off")
plt.suptitle("EduPro — Key Performance Indicators", fontsize=14, fontweight="bold", y=1.05)
plt.tight_layout()
plt.savefig("edupro_charts/00_kpi_summary.png", dpi=150, bbox_inches="tight")
plt.show()
