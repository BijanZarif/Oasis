from matplotlib.pyplot import *

color = ["r", "g", "c", "k", "b"]
#color = ["c", "k", "r", "k", "b"]

#color = ["b", "r", "g", ""]
figure(figsize=(15, 7))
plot([1,3,4,5], [3,3,3,3], label="5M", color=color[0], linewidth=3)
hold("on")
#errorbar([1], [3], yerr=[[2], [3]], fmt="o", label=r"Experiment mean $\pm 95\%$ C.I.", color="b")
plot([1,3,4,5], [3,3,3,3], label="10M", color=color[1], linewidth=3)
plot([1,3,4,5], [3,3,3,3], label="17M", color=color[2], linewidth=3)
plot([1,3,4,5], [3,3,3,3], label="28M", linewidth=3, color=color[3])
plot([1,3,4,5], [3,3,3,3], label="10M P2-P1", linewidth=3, color=color[4])
legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=6, mode="expand",
        borderaxespad=0., fontsize="xx-large")
#show()
savefig("legend.eps")
