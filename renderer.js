// UMD bundles already loaded in index.html
const {
  Box, Container, Typography, Button, Stack, Paper,
  Card, CardContent, CircularProgress, Link
} = MaterialUI;

const { spawn } = require('child_process');
const fs = require('fs');


function App() {
  const [step, setStep] = React.useState("welcome");   // welcome | instructions | upload
  const [data, setData] = React.useState(null);
  const [loading, setLoading] = React.useState(false);
  //OCR
  const runOCR = (filePath) => {
    setLoading(true);
    setData(null);

    const path = require('path');
    const script = path.join(__dirname, 'extract_rx.py');
    const py = spawn('python', [script, filePath]);
    let output = '';

    py.stdout.on('data', (chunk) => {
      output += chunk.toString();
    });
    
    py.stdout.on('end', () => {
      try { 
        // Just set the raw output as data without parsing to JSON
        setData(output.trim());
      } catch (err) { 
        console.error("OCR error:", err);
        alert("Could not process OCR output."); 
      }
      setLoading(false);
    });
    
    py.stderr.on('data', (err) => {
      console.error(err.toString());
    });
  };

  // ---------- Handlers ----------
  const handleFile = (file) => {
    if (!file) return;
    runOCR(file.path);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    handleFile(e.dataTransfer.files[0]);
  };

  const handleSend = () => {
    if (!data) return;
    
    // Since data is now just a text string, we can copy it directly
    navigator.clipboard.writeText(data)
      .then(() => {
        console.log('Text copied to clipboard');
        alert("Text copied to clipboard");
      })
      .catch(err => {
        console.error('Failed to copy text: ', err);
        alert("Failed to copy to clipboard");
      });
  };

  // ---------- Reusable chunks ----------
  const hero = (title, subtitle, actions) =>
    React.createElement(Container, {
      maxWidth: "md",
      sx: { pt: 5, pb: 5, textAlign: "center" }
    }, [
      React.createElement(Typography, { variant: "h1", component: "h1", gutterBottom: true }, title),
      React.createElement(Typography, { variant: "h5", color: "text.secondary", mb: 4 }, subtitle),
      React.createElement(Stack, { direction: "row", spacing: 2, justifyContent: "center" }, actions)
    ]);

  if (step === "welcome") {
    return hero(
      "Welcome to m3dswft",
      "Automating Pharmacy Workflows.",
      [
        React.createElement(Button, {
          variant: "contained", size: "large",
          onClick: () => setStep("instructions")
        }, "Start")
      ]
    );
  }

  if (step === "instructions") {
    return hero(
      "About",
      "Want to extract text from digital faxes or typed prescriptions? " +
      "This tool uses OCR to convert images to text, making it easier to process prescriptions." +
      "Click 'Proceed to Upload' to start.",
      [
        React.createElement(Button, {
          variant: "outlined", size: "large",
          onClick: () => setStep("upload")
        }, "Proceed to Upload"),
        React.createElement(Link, {
          href: "#", underline: "hover",
          onClick: () => setStep("Welcome")
        }, "Back")
      ]
    );
  }

  // Upload / OCR screen
  return React.createElement(Container, { maxWidth: "md", sx: { pt: 5, pb: 10 } }, [

    React.createElement(Stack, { spacing: 5 }, [

      // Drop zone + upload button
      React.createElement(Paper, {
        elevation: 3,
        onDrop: handleDrop,
        onDragOver: e => e.preventDefault(),
        sx: {
          p: 5, textAlign: "center", border: "2px dashedrgb(14, 16, 18)",
          backgroundColor: "#636363", cursor: "pointer"
        }
      }, "Drag & Drop Digital Fax or Typed Prescription Here"),

      React.createElement("input", {
        id: "fileInput", type: "file", accept: ".pdf,.png,.jpg,.jpeg",
        style: { display: 'none' },
        onChange: e => handleFile(e.target.files[0])
      }),
      React.createElement(Button, {
        variant: "contained",
        onClick: () => document.getElementById('fileInput').click()
      }, "Choose file here"),

      // React.createElement(Button, {
      //   variant: "contained",
      //   onClick: () => document.getElementById('fileInput2').click()
      // }, "Choose handwritten file here"), this one we can uncomment later when we have handwriting working.

      // Loading spinner
      loading && React.createElement(Box, { textAlign: "center" },
        React.createElement(CircularProgress, null)
      ),

      // Result card
      data && React.createElement(Card, { id: "results-card" },
        React.createElement(CardContent, null, [
          React.createElement(Typography, { variant: "h5", gutterBottom: true }, 
            "Results:"),
          React.createElement(Typography, { 
            variant: "body1", 
            component: "pre",
            sx: { 
              whiteSpace: "pre-wrap", 
              fontFamily: "monospace",
              backgroundColor: "#f5f5f5",
              p: 2,
              borderRadius: 1
            }
          }, data)
        ])
      ),

      // Send button
      React.createElement(Button, {
        variant: "contained",
        disabled: !data,
        onClick: handleSend
      }, "Copy OCR Results to Clipboard")
    ]),

    // Back link
    React.createElement(Box, { textAlign: "center", mt: 4 },
      React.createElement(Link, {
        href: "#", underline: "hover",
        onClick: () => setStep("instructions")
      }, "Back to Instructions")
    )
  ]);
}

ReactDOM.createRoot(document.getElementById("root"))
  .render(React.createElement(App));
