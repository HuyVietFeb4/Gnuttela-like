import sys
sys.path.append("../")
from src.application.bloom import BloomFilter, KM_BloomFilter, Compact_BloomFilter, Compact_Refined_BloomFilter, Yes_No_BloomFilter
import bloom_test_util
import matplotlib.pyplot as plt

# Prepare storage
iterations = list(range(1, 11))
accuracy_results = {
    "BloomFilter": [], 
    "KM_BloomFilter": [], 
    "Compact_BloomFilter": [], 
    "Compact_Refined_BloomFilter": [], 
    "Yes_No_BloomFilter": []
}
fp_results = {k: [] for k in accuracy_results}
fn_results = {k: [] for k in accuracy_results}

# Run 10 iterations
for i in iterations:
    standard_bf = BloomFilter(10000, 0.01)
    km_bf = KM_BloomFilter(10000, 0.01)
    cm_bf = Compact_BloomFilter(10000, 0.01)
    cm_bf_refined = Compact_Refined_BloomFilter(10000, 0.01)
    yn_bf = Yes_No_BloomFilter(10000, 0.01)

    # Standard
    acc, fp, fn = bloom_test_util.test_accuracy_bloom_filters('dict.csv', BloomFilter, standard_bf)
    accuracy_results["BloomFilter"].append(acc)
    fp_results["BloomFilter"].append(fp)
    fn_results["BloomFilter"].append(fn)

    # KM
    acc, fp, fn = bloom_test_util.test_accuracy_bloom_filters('dict.csv', KM_BloomFilter, km_bf)
    accuracy_results["KM_BloomFilter"].append(acc)
    fp_results["KM_BloomFilter"].append(fp)
    fn_results["KM_BloomFilter"].append(fn)

    # Compact
    acc, fp, fn = bloom_test_util.test_accuracy_bloom_filters('dict.csv', Compact_BloomFilter, cm_bf)
    accuracy_results["Compact_BloomFilter"].append(acc)
    fp_results["Compact_BloomFilter"].append(fp)
    fn_results["Compact_BloomFilter"].append(fn)

    # Compact Refined
    acc, fp, fn = bloom_test_util.test_accuracy_bloom_filters('dict.csv', Compact_Refined_BloomFilter, cm_bf_refined)
    accuracy_results["Compact_Refined_BloomFilter"].append(acc)
    fp_results["Compact_Refined_BloomFilter"].append(fp)
    fn_results["Compact_Refined_BloomFilter"].append(fn)

    # Yes-No (use re-test values)
    acc, fp, fn = bloom_test_util.test_accuracy_bloom_filters('dict.csv', Yes_No_BloomFilter, yn_bf)
    accuracy_results["Yes_No_BloomFilter"].append(acc)
    fp_results["Yes_No_BloomFilter"].append(fp)
    fn_results["Yes_No_BloomFilter"].append(fn)

    print("Iteration", i, "done")

# Plot Accuracy
plt.figure(figsize=(12, 6))
for bf in accuracy_results:
    plt.plot(iterations, accuracy_results[bf], marker='o', label=bf)
plt.title('Bloom Filter Accuracy Across Iterations')
plt.xlabel('Iteration')
plt.ylabel('Accuracy')
plt.legend()
plt.grid(True)
plt.show()

# Plot False Positives
plt.figure(figsize=(12, 6))
for bf in fp_results:
    plt.plot(iterations, fp_results[bf], marker='o', label=bf)
plt.title('Bloom Filter False Positive Rate Across Iterations')
plt.xlabel('Iteration')
plt.ylabel('False Positive Rate')
plt.legend()
plt.grid(True)
plt.show()

# Plot False Negatives
plt.figure(figsize=(12, 6))
for bf in fn_results:
    plt.plot(iterations, fn_results[bf], marker='o', label=bf)
plt.title('Bloom Filter False Negative Rate Across Iterations')
plt.xlabel('Iteration')
plt.ylabel('False Negative Rate')
plt.legend()
plt.grid(True)
plt.show()
