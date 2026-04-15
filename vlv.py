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
    The final film thickness ($t$) depends heavily on the spin speed ($\omega$ in RPM) and the viscosity of the photoresist. 
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
    st.markdown("""
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
        ["1. Spin Coating", "2. Soft Bake", "3. Exposure (Coming Soon)"]
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

    elif step == "3. Exposure (Coming Soon)":
        st.header("Step 3: UV Exposure")
        st.info("Simulation for optical constants and exposure dose will be implemented here.")

# --- TAB 5: QUIZ ---
with tab_quiz:
    st.header("Test Your Knowledge")
    st.markdown("1. Why does the final resist thickness decrease as spin speed increases?")
    st.markdown("2. What is the physical consequence of baking AZ 1505 at 145°C?")