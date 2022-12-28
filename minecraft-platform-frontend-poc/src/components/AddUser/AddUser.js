import './AddUser.css';
import RootDiv from "../../UI/RootDiv";
import PinkCard from "../../UI/PinkCard";
import TextField from "@mui/material/TextField";
import Button from "@mui/material/Button";

const AddUser = () => {
  return (
    <RootDiv>
      <PinkCard SectionHeader="Add New User">
            <div id="AddServerFormEntries">
                <div className="AddServerFormGroup">
                    <label>New Users Username</label>
                    <TextField
                        type="text"
                        InputProps={{
                            inputProps: {
                                max: 100, min: 1, step: 1
                            }
                        }}
                        label="Username"
                    />
                </div>
                <div className="AddServerFormGroup">
                    <label>New Users Password</label>
                    <TextField
                        type="text"
                        InputProps={{
                            inputProps: {
                                max: 100, min: 1, step: 1
                            }
                        }}
                        label="Password"
                    />
                </div>
            </div>

          <div id="AddServerFormEntries">
            <div className="AddServerFormGroup">
                <Button variant="contained">Add User</Button>
            </div>
          </div>
      </PinkCard>
    </RootDiv>
  );
}
export default AddUser
