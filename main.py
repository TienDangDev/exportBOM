import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="BOM & Life Cycle Merger", layout="wide")
st.title("BOM & Life Cycle Data Merger")

# Create columns for layout
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Upload BOM File")
    bom_file = st.file_uploader("Select BOM Excel file (.xlsx or .xls)", type=['xlsx', 'xls'], key="bom")

with col2:
    st.subheader("Upload Life Cycle File")
    life_cycle_file = st.file_uploader("Select Life Cycle Excel file (.xlsx or .xls)", type=['xlsx', 'xls'],
                                       key="life_cycle")

with col3:
    st.subheader("MTS List")
    mts_input = st.text_area(
        "Enter MTS codes (one per line or comma-separated):",
        height=150,
        placeholder="MTS001\nMTS002\nMTS003\n\nOr: MTS001,MTS002,MTS003"
    )

# Process when all inputs are provided
if bom_file and life_cycle_file and mts_input:
    try:
        # Parse MTS list
        if ',' in mts_input:
            mts_list = [code.strip() for code in mts_input.split(',')]
        else:
            mts_list = [code.strip() for code in mts_input.split('\n')]

        mts_list = [code for code in mts_list if code]  # Remove empty strings

        if not mts_list:
            st.error("Please enter at least one MTS code")
        else:
            # Read files
            bom_df = pd.read_excel(bom_file)
            life_cycle_df = pd.read_excel(life_cycle_file)

            st.success(f"✓ Files loaded successfully")
            st.info(f"MTS codes to filter: {', '.join(mts_list)}")

            # Filter BOM by MTS codes
            bom_filtered = bom_df[bom_df['MTS'].isin(mts_list)].copy()

            if bom_filtered.empty:
                st.warning("No rows found matching the provided MTS codes")
            else:
                # Merge with Life Cycle data
                output_df = bom_filtered.merge(
                    life_cycle_df[['PN', 'Limit']],
                    on='PN',
                    how='left'
                )

                # Create output table with specified columns
                output_df_final = pd.DataFrame({
                    "SW /HCA": "",
                    "Product Lines": output_df['ProductLines'],
                    "StationTypes": output_df['StationTypes'],
                    "MTS": output_df['MTS'],
                    "PN (SFG\\SA)": output_df['PN (SFG\\SA)'],
                    "PN": output_df['PN'],
                    "Alternative PN": output_df['Alternative PN'],
                    "Description": output_df['Description'],
                    "Group": output_df['Group'],
                    "BOM Quantity": output_df['Quantity'],
                    "Life Cycle Limit": output_df['Limit']
                })

                # Display results
                st.subheader("Preview")
                st.dataframe(output_df_final, use_container_width=True)

                st.success(f"✓ Processed {len(output_df_final)} rows")

                # Download button
                csv_buffer = io.StringIO()
                output_df_final.to_csv(csv_buffer, index=False)
                csv_data = csv_buffer.getvalue()

                st.download_button(
                    label="📥 Download Output CSV",
                    data=csv_data,
                    file_name="output.csv",
                    mime="text/csv"
                )

                # Alternative: Excel format download
                excel_buffer = io.BytesIO()
                output_df_final.to_excel(excel_buffer, index=False, sheet_name="Output")
                excel_buffer.seek(0)

                st.download_button(
                    label="📥 Download Output Excel",
                    data=excel_buffer.getvalue(),
                    file_name="output.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

    except KeyError as e:
        st.error(f"Column not found: {e}. Please check that your files have the expected columns.")
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")