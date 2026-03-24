import json

class TokenTracker:
    def __init__(self):
        self.data = {}

    def add(self, agent, scene, input_tokens, output_tokens):
        if agent not in self.data:
            self.data[agent] = {}
        if scene not in self.data[agent]:
            self.data[agent][scene] = {"input": 0, "output": 0}
        self.data[agent][scene]["input"] += input_tokens
        self.data[agent][scene]["output"] += output_tokens

    def get_agent_scene(self, agent, scene):
        return self.data.get(agent, {}).get(scene, {"input": 0, "output": 0})

    def get_agent_total(self, agent):
        total_input = sum(s["input"] for s in self.data.get(agent, {}).values())
        total_output = sum(s["output"] for s in self.data.get(agent, {}).values())
        return {"input": total_input, "output": total_output}

    def get_scene_total(self, scene):
        total_input = sum(self.data[a][scene]["input"] for a in self.data if scene in self.data[a])
        total_output = sum(self.data[a][scene]["output"] for a in self.data if scene in self.data[a])
        return {"input": total_input, "output": total_output}

    def get_grand_total(self):
        total_input = sum(self.get_agent_total(a)["input"] for a in self.data)
        total_output = sum(self.get_agent_total(a)["output"] for a in self.data)
        return {"input": total_input, "output": total_output}

    def print_report(self):
        print("\n=== Token Usage Report ===")
        for agent in self.data:
            print(f"\nAgent: {agent}")
            for scene in self.data[agent]:
                d = self.data[agent][scene]
                print(f"  Scene: {scene} | Input: {d['input']} | Output: {d['output']}")
            total = self.get_agent_total(agent)
            print(f"  Agent Total | Input: {total['input']} | Output: {total['output']}")
        grand = self.get_grand_total()
        print(f"\nGrand Total | Input: {grand['input']} | Output: {grand['output']}\n")

    def save(self, path):
        with open(path, "w") as f:
            json.dump(self.data, f, indent=2)