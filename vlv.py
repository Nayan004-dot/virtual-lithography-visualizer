import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# 1. Page Configuration
st.set_page_config(page_title="Virtual Lithography Visualizer", layout="wide")

# Constants (Restricted to AZ 1505)
RESIST_CONSTANTS = {"AZ 1505": 31.62}

# Initialize session state 
if 'current_thickness' not in st.session_state:
    st.session_state.current_thickness = 0.0
if 'selected_resist' not in st.session_state:
    st.session_state.selected_resist = "AZ 1505"
if 'resist_status' not in st.session_state:
    st.session_state.resist_status = "Unbaked"

# 2. Sidebar Setup
st.sidebar.title("Lithography Process")
st.sidebar.subheader("Material Setup")
resist_type = st.sidebar.selectbox("Select Photoresist:", list(RESIST_CONSTANTS.keys()))
st.session_state.selected_resist = resist_type

st.sidebar.markdown("---")
step = st.sidebar.radio(
    "Select Process Step:",
    ["1. Spin Coating", "2. Soft Bake", "3. Exposure (Coming Soon)"]
)

# 3. Main Logic
if step == "1. Spin Coating":
    st.header("Step 1: Photoresist Spin Coating")
    st.sidebar.markdown("---")
    st.sidebar.subheader("Process Parameters")
    
    rpm = st.sidebar.slider("Spin Speed (RPM)", min_value=500, max_value=5000, value=3000, step=100)
    
    # Calculate thickness
    k_val = RESIST_CONSTANTS[st.session_state.selected_resist]
    thickness_um = k_val / np.sqrt(rpm)
    st.session_state.current_thickness = thickness_um 
    st.session_state.resist_status = "Unbaked" # Reset status on new spin
    
    col1, col2 = st.columns(2)
    col1.metric(label="Spin Speed", value=f"{rpm} RPM")
    col2.metric(label=f"Calculated Film Thickness", value=f"{thickness_um:.3f} µm")
        
    st.markdown("---")
    st.subheader("Wafer Cross-Section View")
    
    fig, ax = plt.subplots(figsize=(10, 4))
    x = np.linspace(0, 10, 100)
    
    ax.fill_between(x, 0, -2, color='#A9A9A9', label='Silicon Substrate')
    ax.fill_between(x, 0, thickness_um, color='#FF4500', alpha=0.7, label=f'{st.session_state.selected_resist} ({thickness_um:.2f} µm)')
    
    ax.set_ylim(-2.5, 3.0) 
    ax.set_xlim(0, 10)
    ax.set_ylabel("Thickness (µm)")
    ax.set_xticks([])
    ax.legend(loc="upper right")
    ax.grid(True, axis='y', linestyle='--', alpha=0.5)
    st.pyplot(fig)

elif step == "2. Soft Bake":
    st.header("Step 2: Soft Bake")
    st.markdown("Evaporating solvent to densify the film. Adjust temperature to see effects on the photoresist.")
    
    # Check if user skipped step 1
    if st.session_state.current_thickness == 0.0:
        st.warning("⚠️ Please go to Step 1 and spin coat the wafer first!")
        st.stop()

    st.sidebar.markdown("---")
    st.sidebar.subheader("Bake Parameters")
    
    # Expanded slider to allow for process failure
    temp = st.sidebar.slider("Temperature (°C)", min_value=70, max_value=150, value=100, step=5)
    time_sec = st.sidebar.slider("Time (seconds)", min_value=30, max_value=120, value=90, step=10)
    
    # Cause and Effect Logic
    pr_color = '#FF4500' # Default Orange
    shrinkage_factor = 1.0
    
    if temp < 90:
        st.info("ℹ️ **Underbaked:** Film contains too much solvent. May cause adhesion loss or 'dark erosion' during development.")
        st.session_state.resist_status = "Underbaked"
        shrinkage_factor = 0.98 # Barely shrinks
        pr_color = '#FFA07A' # Light salmon (looks "wet")
        
    elif 90 <= temp <= 100:
        st.success("✅ **Optimal (Si Substrate):** Ideal solvent evaporation for standard processing.")
        st.session_state.resist_status = "Optimal"
        shrinkage_factor = 0.90 # Normal 10% shrinkage
        
    elif 100 < temp <= 110:
        st.success("✅ **Optimal (Metals):** High-end temperature ideal for maximizing adhesion to metal substrates.")
        st.session_state.resist_status = "Optimal"
        shrinkage_factor = 0.88 
        pr_color = '#FF0000' # Deep red
        
    elif 110 < temp < 140:
        st.warning("⚠️ **Degraded:** Photoactive compound (PAC) is breaking down. Exposure step will be compromised.")
        st.session_state.resist_status = "Degraded"
        shrinkage_factor = 0.85 
        pr_color = '#8B4513' # Saddle brown (burning)
        
    elif temp >= 140:
        st.error("🚨 **CRITICAL FAILURE: Charred.** Resist has cross-linked and charred. It is no longer photosensitive and will not dissolve in solvent removers.")
        st.session_state.resist_status = "Charred"
        shrinkage_factor = 0.80 
        pr_color = '#2F4F4F' # Dark slate gray (charred)

    baked_thickness = st.session_state.current_thickness * shrinkage_factor

    col1, col2, col3 = st.columns(3)
    col1.metric(label="Initial Thickness", value=f"{st.session_state.current_thickness:.3f} µm")
    col2.metric(label="Post-Bake Thickness", value=f"{baked_thickness:.3f} µm", delta=f"-{st.session_state.current_thickness - baked_thickness:.3f} µm")
    col3.metric(label="Resist Status", value=st.session_state.resist_status)

    st.markdown("---")
    st.subheader("Wafer Cross-Section View")
    
    # Visualization updating based on bake results
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
    if st.session_state.resist_status in ["Degraded", "Charred"]:
        st.error(f"Cannot expose wafer. The photoresist was {st.session_state.resist_status.lower()} during the Soft Bake step.")
    else:
        st.info("Resist is ready for UV exposure modeling.")