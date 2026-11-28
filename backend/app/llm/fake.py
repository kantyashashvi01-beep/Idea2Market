import re
from typing import Type, TypeVar, Literal
from pydantic import BaseModel
from app.schemas.pipeline_schemas import (
    ClarificationQuestionsOutput,
    ClarificationQuestionItem,
    RequirementsOutput,
    RequirementGeneratedItem,
    ArchitectureOutput,
    SubsystemGeneratedItem,
    InterfaceGeneratedItem,
    ProposedBOMOutput,
    ProposedBOMItem,
    RoadmapAndRisksOutput,
    RoadmapStageGeneratedItem,
    RiskGeneratedItem,
)

T = TypeVar("T", bound=BaseModel)


class FakeLLMClient:
    """
    Deterministic client returning schema-compliant test fixtures.
    Used for local testing and CI without calling third-party APIs.
    """

    def generate_json(
        self,
        *,
        system: str,
        user: str,
        schema: Type[T],
        model_role: Literal["strong", "fast"] = "fast",
    ) -> T:
        if schema is ClarificationQuestionsOutput:
            return ClarificationQuestionsOutput(
                questions=[
                    ClarificationQuestionItem(
                        question="What is the expected operating terrain and slope (e.g. wet clay, tilled soil, furrows)?",
                        context_reason="Crucial for selecting wheel diameter, motor stall torque, and ground clearance.",
                    ),
                    ClarificationQuestionItem(
                        question="What is the required continuous runtime between battery charges (e.g. 2 hours vs 6 hours)?",
                        context_reason="Determines LiFePO4 battery pack capacity (Ah) and need for solar trickle top-up.",
                    ),
                    ClarificationQuestionItem(
                        question="What is the spraying or weeding payload capacity (e.g. 5-litre spot spray tank)?",
                        context_reason="Directly dictates chassis structural load rating and pump flow rate specifications.",
                    ),
                    ClarificationQuestionItem(
                        question="What navigation accuracy is required (meter-level GPS vs centimeter RTK)?",
                        context_reason="Decides between low-cost GPS NEO-M8N and dual-frequency RTK GNSS.",
                    ),
                ]
            )  # type: ignore

        if schema is RequirementsOutput:
            return RequirementsOutput(
                problem_restatement="Smallholder Indian farmers require an affordable, low-maintenance autonomous robotic rover capable of navigating crop rows, identifying unwanted weeds, and targeted micro-spraying without compacting farm soil.",
                target_users="Small and marginal farmers, agricultural cooperatives, and research agronomists.",
                requirements=[
                    RequirementGeneratedItem(kind="functional", text="Navigate farm rows autonomously while avoiding crops and obstacles", priority="high"),
                    RequirementGeneratedItem(kind="functional", text="Detect weeds and trigger targeted spot-spray solenoid valve", priority="high"),
                    RequirementGeneratedItem(kind="functional", text="Operate continuously for at least 3 hours per battery charge", priority="high"),
                    RequirementGeneratedItem(kind="constraint", text="Operate in temperatures up to 45°C with dust and water spray resistance (IP65)", priority="high"),
                    RequirementGeneratedItem(kind="constraint", text="Chassis track width must fit standard Indian crop furrow spacing (450mm - 600mm)", priority="medium"),
                    RequirementGeneratedItem(kind="assumption", text="Operation occurs during daylight in un-flooded field conditions", priority="low"),
                ],
            )  # type: ignore

        if schema is ArchitectureOutput:
            return ArchitectureOutput(
                subsystems=[
                    SubsystemGeneratedItem(
                        name="Chassis & Drivetrain",
                        purpose="Mechanical platform, suspension, high-torque planetary motors, and lug wheels",
                        interfaces_with=["Power System", "Low-Level MCU Controller"],
                    ),
                    SubsystemGeneratedItem(
                        name="Compute & Vision Processing",
                        purpose="Onboard SBC running computer vision weed detection and obstacle segmentation",
                        interfaces_with=["Low-Level MCU Controller", "Sensors & Camera", "Power System"],
                    ),
                    SubsystemGeneratedItem(
                        name="Power & Energy Management",
                        purpose="LiFePO4 battery pack, BMS protection, fuse block, and buck regulation",
                        interfaces_with=["All Subsystems"],
                    ),
                    SubsystemGeneratedItem(
                        name="Navigation & Sensor Suite",
                        purpose="Waypoint guidance, obstacle ranging (LiDAR/ultrasonic), and heading IMU",
                        interfaces_with=["Compute & Vision Processing"],
                    ),
                    SubsystemGeneratedItem(
                        name="Targeted Spraying Payload",
                        purpose="Liquid chemical tank, 12V diaphragm pump, and solenoid nozzle assembly",
                        interfaces_with=["Low-Level MCU Controller", "Power System"],
                    ),
                ],
                interfaces=[
                    InterfaceGeneratedItem(from_subsystem="Power System", to_subsystem="Chassis & Drivetrain", description="12V high-current DC via fused circuit"),
                    InterfaceGeneratedItem(from_subsystem="Compute & Vision Processing", to_subsystem="Low-Level MCU Controller", description="UART/USB serial command stream"),
                    InterfaceGeneratedItem(from_subsystem="Low-Level MCU Controller", to_subsystem="Chassis & Drivetrain", description="Dual PWM motor driver signals"),
                    InterfaceGeneratedItem(from_subsystem="Navigation & Sensor Suite", to_subsystem="Compute & Vision Processing", description="I2C/UART sensor telemetry"),
                    InterfaceGeneratedItem(from_subsystem="Low-Level MCU Controller", to_subsystem="Targeted Spraying Payload", description="Optocoupled 12V relay pump trigger"),
                ],
            )  # type: ignore

        if schema is ProposedBOMOutput:
            # Extract available component IDs if listed in prompt
            cat_ids = [int(m) for m in re.findall(r"\[ID\s*:\s*(\d+)\]", user)]
            if not cat_ids:
                cat_ids = [1, 3, 11, 21, 29, 31, 37, 39, 41, 45, 48, 57, 67, 77, 85, 95, 97, 101, 107]

            # Pick matching items from extracted list
            chosen_items = []
            for cid in cat_ids[:15]:
                chosen_items.append(
                    ProposedBOMItem(
                        component_id=cid,
                        quantity=2 if cid in [11, 67, 57] else 1,
                        role_in_design=f"Core rover component (Catalogue ID {cid})",
                        confidence="high",
                    )
                )

            return ProposedBOMOutput(
                items=chosen_items,
                assumptions_note="All items selected strictly from the verified agricultural rover catalogue.",
            )  # type: ignore

        if schema is RoadmapAndRisksOutput:
            return RoadmapAndRisksOutput(
                stages=[
                    RoadmapStageGeneratedItem(position=1, title="Phase 1: Proof of Concept Bench Testing", deliverable="Motor driver testing, benchtop computer vision weed classification, and power telemetry validation", duration_note="2 weeks"),
                    RoadmapStageGeneratedItem(position=2, title="Phase 2: Rolling Chassis & Skid-Steer Validation", deliverable="Assembled aluminium extrusion frame, wheel gearboxes, and manual remote teleoperation in dirt track", duration_note="3 weeks"),
                    RoadmapStageGeneratedItem(position=3, title="Phase 3: Sensor Fusion & Autonomous Traversal", deliverable="Integration of GPS/IMU waypoint following, obstacle avoidance stopping, and battery endurance profiling", duration_note="4 weeks"),
                    RoadmapStageGeneratedItem(position=4, title="Phase 4: Field Agricultural Spray Trial", deliverable="Plumbed 5L spot spray payload, targeted water test over weeds, and DFM review with farming mentors", duration_note="3 weeks"),
                ],
                risks=[
                    RiskGeneratedItem(
                        title="Mud and Soil Ingress into Motor Gearbox Bearings",
                        severity="high",
                        reason="Wet agricultural soil contains fine abrasive grit that rapidly damages unsealed planetary gearboxes and leads to motor lockup.",
                        needs_expert=True,
                    ),
                    RiskGeneratedItem(
                        title="Vibration-Induced Electrical Connector Disconnects",
                        severity="medium",
                        reason="Traversing uneven farm furrows introduces sustained low-frequency vibration that loosens standard Dupont wire jumpers.",
                        needs_expert=True,
                    ),
                    RiskGeneratedItem(
                        title="Thermal Throttling of Vision SBC Inside Sealed Enclosure",
                        severity="medium",
                        reason="Sunlight ambient temperatures in Indian agricultural fields can exceed 42°C, causing compute overheating in sealed IP65 containers without forced cooling.",
                        needs_expert=True,
                    ),
                    RiskGeneratedItem(
                        title="GPS Multipath Occlusion Under Tree Canopies",
                        severity="low",
                        reason="Dense foliage degrades standard GPS reception, requiring reliance on IMU odometry and vision row tracking.",
                        needs_expert=False,
                    ),
                ],
            )  # type: ignore

        raise ValueError(f"FakeLLMClient has no canned response for schema: {schema}")
