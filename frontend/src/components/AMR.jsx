import { useEffect, useState } from "react"
import Plot from "react-plotly.js"

async function load_data(organism) {
    console.log("Loading data for organism:", organism)  // Debugging statement to check the value of organism
    // set with parameter
    const params = new URLSearchParams({
        organism: organism
    })
    const url = `http://localhost:8000/amr?${params}`

    const result = await fetch(url)
    const json_result = await result.json()

    return json_result
}


function AMR() {
    // initialize state variables
    const [data, setData] = useState(null)
    const [selectedOrganism, setSelectedOrganism] = useState('All Organisms')

    // fetch data
    useEffect(() => {
        const fetchData = async (selectedOrganism) => {
            const result = await load_data(selectedOrganism)
            setData(result)
        }
        fetchData(selectedOrganism)
    }, [selectedOrganism])

    return (
        <>
        <div style={{alignItems: "center", textAlign: "center"}}>
            <h3>Antibiotic Resistance Overview</h3>
        </div>

        {/*Create organism selection*/}
        <div style={{padding: '20px', paddingLeft: '50px'}}>
            <form>
                <label>Choose an organism:
                    <select value={selectedOrganism} onChange={(e) => setSelectedOrganism(e.target.value)}>
                        <option value='All Organisms'>All Organisms</option>
                        {data && data.organisms.map((organism) => (
                            <option key={organism} value={organism}>{organism}</option>
                        ))}
                    </select>
                </label>
            </form>
        </div>

        <div>
            {data && (
                <Plot
                    data={[
                        {
                            x: Object.keys(data.drug_class_counts),
                            y: Object.values(data.drug_class_counts),
                            type: 'bar'
                        }
                    ]}
                    layout={{
                        title: {
                            text: `Number of Samples by Drug Class Resistance<br>(${selectedOrganism})`
                        },
                        xaxis: {
                            title: {
                                text: 'Drug Class'
                            }
                        },
                        yaxis: {
                            title: {
                                text: 'Number of Samples'
                            }
                        },
                        margin: {
                            t: 35,
                            b: 100
                        }
                    }}
                />
                )}
        </div>
        </>
    )
}

export default AMR