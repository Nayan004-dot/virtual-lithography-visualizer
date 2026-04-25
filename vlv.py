import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# 1. Page Configuration
st.set_page_config(page_title="Virtual Lithography Lab", layout="wide")

# Constants 
RESIST_CONSTANTS = {"AZ 1505": 31.62}

# Initialize session state 
if 'current_thickness' not in st.session_state:
    st.session_state.current_thickness = 0.0
if 'selected_resist' not in st.session_state:
    st.session_state.selected_resist = "AZ 1505"
if 'resist_status' not in st.session_state:
    st.session_state.resist_status = "Unbaked"

# --- MAIN VIRTUAL LAB LAYOUT ---
st.title("🔬 Virtual Lab: Photolithography Process")
st.markdown("Explore the deposition and baking of positive photoresists on a silicon substrate.")

# Create the standard Virtual Lab Tabs
tab_aim, tab_theory, tab_procedure, tab_simulation, tab_quiz = st.tabs([
    "🎯 Aim", "📚 Theory", "📝 Procedure", "⚙️ Simulation", "🧠 Quiz"
])

# --- TAB 1: AIM ---
with tab_aim:
    st.header("Objective")
    st.markdown("""
    The aim of this virtual experiment is to:
    * Understand the empirical relationship between spin speed (RPM) and photoresist film thickness.
    * Simulate the spin coating of AZ 1505 positive photoresist on a bare silicon wafer.
    * Analyze the thermal effects of the Soft Bake process on film densification and photoactive compound stability.
    """)

# --- TAB 2: THEORY ---
with tab_theory:
    st.header("Theoretical Background")
    st.subheader("1. Spin Coating")
    st.markdown("""
Spin coating is used to deposit uniform thin films onto flat substrates. 
The final film thickness ($t$) depends heavily on the spin speed ($\\omega$ in RPM) and the viscosity of the photoresist. 
For AZ 1505, this can be approximated using the inverse square root law:

$t = \\frac{k}{\\sqrt{\\omega}}$

Where $k$ is a resist-specific constant calibrated to yield ~0.5 µm at 4000 RPM.
""")
    st.subheader("2. Soft Bake (Pre-Bake)")
    st.markdown("""
    The soft bake step evaporates the remaining casting solvent, densifying the film. 
    * **Optimal Range:** 90°C to 110°C. 
    * Temperatures above 110°C risk thermally degrading the Photoactive Compound (PAC).
    * Temperatures above 140°C cause the resist to cross-link and char, rendering it useless for UV exposure.
    """)

# --- TAB 3: PROCEDURE ---
with tab_procedure:
    st.header("Experiment Instructions")
    st.markdown(r"""
    1. Navigate to the **Simulation** tab.
    2. In the left sidebar, ensure **AZ 1505** is selected.
    3. Select **Step 1: Spin Coating**. Adjust the RPM slider and observe the inverse relationship with film thickness on the cross-section graph.
    4. Select **Step 2: Soft Bake**. Experiment with different temperatures to find the optimal process window. Observe what happens when you exceed 110°C.
    """)

# --- TAB 4: SIMULATION (Our existing interactive code) ---
with tab_simulation:
    # Sidebar Setup specifically for the simulation
    st.sidebar.title("Lab Controls")
    resist_type = st.sidebar.selectbox("Select Photoresist:", list(RESIST_CONSTANTS.keys()))
    st.session_state.selected_resist = resist_type
    
    st.sidebar.markdown("---")
    step = st.sidebar.radio(
        "Select Process Step:",
        [
            "1. Spin Coating", 
            "2. Soft Bake", 
            "3. Maskless Exposure", 
            "4. Post-Exposure Bake (PEB)",
            "5. Development"
        ]
    )

    # --- Step 1 Logic ---
    if step == "1. Spin Coating":
        st.header("Step 1: Photoresist Spin Coating")
        
        rpm = st.sidebar.slider("Spin Speed (RPM)", min_value=500, max_value=5000, value=3000, step=100)
        
        k_val = RESIST_CONSTANTS[st.session_state.selected_resist]
        thickness_um = k_val / np.sqrt(rpm)
        st.session_state.current_thickness = thickness_um 
        st.session_state.resist_status = "Unbaked" 
        
        col1, col2 = st.columns(2)
        col1.metric("Spin Speed", f"{rpm} RPM")
        col2.metric("Calculated Film Thickness", f"{thickness_um:.3f} µm")
            
        st.markdown("---")
        fig, ax = plt.subplots(figsize=(10, 4))
        x = np.linspace(0, 10, 100)
        
        ax.fill_between(x, 0, -2, color='#A9A9A9', label='Silicon Substrate')
        ax.fill_between(x, 0, thickness_um, color='#FF4500', alpha=0.7, label=f'AZ 1505 ({thickness_um:.2f} µm)')
        
        ax.set_ylim(-2.5, 3.0) 
        ax.set_xlim(0, 10)
        ax.set_ylabel("Thickness (µm)")
        ax.set_xticks([])
        ax.legend(loc="upper right")
        ax.grid(True, axis='y', linestyle='--', alpha=0.5)
        st.pyplot(fig)

    # --- Step 2 Logic ---
    elif step == "2. Soft Bake":
        st.header("Step 2: Soft Bake")
        
        if st.session_state.current_thickness == 0.0:
            st.warning("⚠️ Please execute Step 1 (Spin Coating) first!")
        else:
            temp = st.sidebar.slider("Temperature (°C)", min_value=70, max_value=150, value=100, step=5)
            time_sec = st.sidebar.slider("Time (seconds)", min_value=30, max_value=120, value=90, step=10)
            
            pr_color = '#FF4500' 
            shrinkage_factor = 1.0
            
            if temp < 90:
                st.session_state.resist_status = "Underbaked"
                shrinkage_factor = 0.98 
                pr_color = '#FFA07A' 
            elif 90 <= temp <= 100:
                st.session_state.resist_status = "Optimal"
                shrinkage_factor = 0.90 
            elif 100 < temp <= 110:
                st.session_state.resist_status = "Optimal"
                shrinkage_factor = 0.88 
                pr_color = '#FF0000' 
            elif 110 < temp < 140:
                st.session_state.resist_status = "Degraded"
                shrinkage_factor = 0.85 
                pr_color = '#8B4513' 
            elif temp >= 140:
                st.session_state.resist_status = "Charred"
                shrinkage_factor = 0.80 
                pr_color = '#2F4F4F' 

            baked_thickness = st.session_state.current_thickness * shrinkage_factor

            col1, col2, col3 = st.columns(3)
            col1.metric("Initial Thickness", f"{st.session_state.current_thickness:.3f} µm")
            col2.metric("Post-Bake Thickness", f"{baked_thickness:.3f} µm", delta=f"-{st.session_state.current_thickness - baked_thickness:.3f} µm")
            col3.metric("Resist Status", st.session_state.resist_status)

            st.markdown("---")
            fig, ax = plt.subplots(figsize=(10, 4))
            x = np.linspace(0, 10, 100)
            
            ax.fill_between(x, 0, -2, color='#A9A9A9', label='Silicon Substrate')
            ax.fill_between(x, 0, baked_thickness, color=pr_color, alpha=0.9, label=f'AZ 1505 ({st.session_state.resist_status})')
            
            ax.set_ylim(-2.5, 3.0) 
            ax.set_xlim(0, 10)
            ax.set_ylabel("Thickness (µm)")
            ax.set_xticks([])
            ax.legend(loc="upper right")
            ax.grid(True, axis='y', linestyle='--', alpha=0.5)
            st.pyplot(fig)

    # --- Step 3 Logic: Maskless Exposure ---
    elif step == "3. Maskless Exposure":
        st.header("Step 3: Direct Write Exposure (uMLA)")
        st.markdown("Simulating the **uMLA maskless aligner** using a 365 nm UV light source.")
        
        if st.session_state.resist_status in ["Degraded", "Charred", "Unbaked"]:
            st.error(f"Cannot expose wafer. The photoresist is currently {st.session_state.resist_status.lower()}.")
        else:
            st.sidebar.markdown("---")
            st.sidebar.subheader("uMLA Parameters")
            
            # Scan Mode Options 
            scan_mode = st.sidebar.radio("Scan Mode", ["Vector Scan", "Raster Scan"])
            pattern_type = st.sidebar.selectbox("Digital Write Pattern", ["Single Trench", "Double Trench", "Dense Grating"])
            
            # Dose and Defocus based on lab manual specs
            dose = st.sidebar.slider("Exposure Dose (mJ/cm²)", min_value=20, max_value=200, value=90, step=10)
            defocus = st.sidebar.slider("Defocus (µm)", min_value=-20, max_value=20, value=0, step=5)
            
            # Display Theoretical Impact of Defocus
            if defocus == 0:
                st.success("✅ **Optimal focus:** Produces sharp, high-resolution features.")
            elif defocus > 0:
                st.info("ℹ️ **Positive defocus:** Beam focused above resist. Increases spot size, useful for larger features.")
            else:
                st.info("ℹ️ **Negative defocus:** Beam focused below resist. Can improve sidewall angles.")

            # 1. Create the sharp 1D digital mask array (Perfect Focus)
            x = np.linspace(0, 10, 500) # High resolution for smooth plotting
            base_profile = np.zeros_like(x)
            
            if pattern_type == "Single Trench":
                base_profile[(x > 4) & (x < 6)] = 1.0
            elif pattern_type == "Double Trench":
                base_profile[(x > 2) & (x < 4)] = 1.0
                base_profile[(x > 6) & (x < 8)] = 1.0
            elif pattern_type == "Dense Grating":
                for i in np.arange(1, 10, 1.5):
                    base_profile[(x > i) & (x < i + 0.6)] = 1.0

            # 2. Simulate Defocus (Beam Spread)
            # Scaling the blur effect down slightly so it remains visible on a 10um plot
            blur_amount = abs(defocus) 
            if blur_amount > 0:
                window_size = int(blur_amount * 2.5) 
                if window_size > 0:
                    window = np.ones(window_size) / window_size
                    exposure_profile = np.convolve(base_profile, window, mode='same')
                    # Defocus lowers peak intensity
                    peak_reduction = max(0.2, 1.0 - (blur_amount * 0.03))
                    exposure_profile = exposure_profile * peak_reduction
            else:
                exposure_profile = base_profile

            st.session_state.received_dose = exposure_profile * dose
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Operating Mode", scan_mode)
            col2.metric("Laser Dose", f"{dose} mJ/cm²")
            col3.metric("Defocus Offset", f"{defocus} µm")

            st.markdown("---")
            fig, ax = plt.subplots(figsize=(10, 4))
            
            baked_thickness = st.session_state.current_thickness * 0.90 
            
            # Substrate and Unexposed Resist
            ax.fill_between(x, 0, -2, color='#A9A9A9', label='Silicon Substrate')
            ax.fill_between(x, 0, baked_thickness, color='#FF0000', alpha=0.8, label='Unexposed AZ 1505')
            
            # Exposed Resist (Chemical Reaction)
            # A chemical reaction occurs between the resist and the light[cite: 292].
            # Only the exposed areas undergo a chemical reaction[cite: 293].
            exposed_thickness = np.where(exposure_profile > 0.05, baked_thickness, 0)
            ax.fill_between(x, 0, exposed_thickness, color='#FFFF00', alpha=np.clip(exposure_profile, 0, 1), label='Reacted AZ 1505')
            
            # Laser Intensity Curve
            ax.plot(x, exposure_profile * (baked_thickness + 1.0), color='blue', linestyle='-', linewidth=2, label='365nm Laser Profile')
            
            ax.set_ylim(-2.5, 4.5) 
            ax.set_xlim(0, 10)
            ax.set_ylabel("Thickness / Intensity")
            ax.set_xticks([])
            ax.legend(loc="upper right", fontsize='small')
            ax.grid(True, axis='y', linestyle='--', alpha=0.5)
            st.pyplot(fig)

# --- TAB 5: QUIZ ---
with tab_quiz:
    st.header("Test Your Knowledge")
    st.markdown("1. Why does the final resist thickness decrease as spin speed increases?")
    st.markdown("2. What is the physical consequence of baking AZ 1505 at 145°C?")