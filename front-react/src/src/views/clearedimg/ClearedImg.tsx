import React, { Component } from "react";
import { 
  Input, Chip, Checkbox, FormControlLabel, Avatar, IconButton, Button, Grid, Card, CardActionArea, CardContent, 
  Drawer, Box, ToggleButtonGroup, ToggleButton 
} from '@mui/material';
import { AddCircle, RemoveCircle, Search, CompareArrows, Verified, Crop, Close, CropOriginal } from '@mui/icons-material';

import { StateTypes } from 'types';
import API from 'api';
import styles from './clearedimg.module.scss';



function getText(type:string) {
  const LANG = process.env.LANGUAGE;

  if (type === "label_placeholder") {
    if (LANG === "en")      return 'input label';
    else if (LANG === "ko") return 'label 입력';
  } else if (type === "value_placeholder") {
    if (LANG === "en")      return 'input value';
    else if (LANG === "ko") return '값 입력';
  } else if (type === "checkbox_include") {
    if (LANG === "en")      return 'check if input included in value';
    else if (LANG === "ko") return '입력값이 값에 포함된다면 체크';
  } else if (type === "search") {
    if (LANG === "en")      return 'SEARCH';
    else if (LANG === "ko") return '검색';
  }
}

class ClearedImg extends Component<StateTypes.ClearedImgProps, StateTypes.ClearedImgState> {
  constructor(props:StateTypes.ClearedImgProps) {
    super(props);
    this.state = {
      search_condition: [ { label: "", value: "", include: false, showchip: false } ],
      result: [],
      selected_res: null,
      detail_view_type_view: "compare_view",
      detail_view_type_tool: []
    }
  }

  checkInputDone(idx:number) {
    let _search_cond = this.state.search_condition.slice();

    (_search_cond[idx] as any).showchip = true;

    this.setState({ search_condition: _search_cond });
  }

  changeSearchCond(idx:number, type:"label"|"value"|"include"|"showchip", value:string|boolean, __cb__?:()=>void) {
    let _search_cond = this.state.search_condition.slice();
    
    if (type === "showchip" && (_search_cond[idx] as any).label === "")
      return;

    (_search_cond[idx] as any)[type] = value;

    this.setState({ search_condition: _search_cond }, __cb__);
  }

  addSearchCond() {
    let _search_cond = this.state.search_condition.slice();
    _search_cond.push({ label: "", value: "", include: false, showchip: false });
    this.setState({ search_condition: _search_cond });
  }

  removeSearchCond(idx:number) {
    let _search_cond = this.state.search_condition.slice();
    _search_cond.splice(idx, 1);
    this.setState({ search_condition: _search_cond });
  }

  search() {
    this.props.setAppState("loading", true, () => {
      let filter:any = {};
      for (let k in this.state.search_condition) {
        let item = this.state.search_condition[k];
        if (!!item.label === false)
          continue;

        if (item.include) {
          filter[item.label] = { "$regex": item.value }
        } else {
          filter[item.label] = item.value;
        }
      }

      API.getimg.cleared(filter, (err, res) => {
        this.props.setAppState('loading', false, () => {
          this.setState({ result: res });
        })
      })
    })
  }

  setDetailViewType(e:React.MouseEvent, type:string, newval:string|string[]) {
    e.preventDefault();

    if (type === "view") {
      if (!!newval)
        this.setState({ detail_view_type_view: newval as string });
    } else if (type === "tool") {
      this.setState({ detail_view_type_tool: newval as string[] });
    }
  }


  render(): React.ReactNode {
    return (
      <>
        {this.state.search_condition.map((val, idx) => (
          <div className={styles.search_content}>
            {!val.showchip ? (
              <Input 
                id={`clearedimg_label_${idx}`}
                multiline={false} 
                placeholder={getText("label_placeholder")} 
                value={val.label} 
                onBlur={() => this.changeSearchCond(idx, "showchip", true)}
                onChange={(e) => this.changeSearchCond(idx, "label", e.target.value)} 
              />
            ) : (
              <Chip 
                variant="outlined" 
                color="primary" 
                avatar={<Avatar>L</Avatar>} 
                label={val.label} 
                onDoubleClick={(e) => this.changeSearchCond(idx, "showchip", false, () => {
                  document.getElementById(`clearedimg_label_${idx}`)?.focus();
                })}
              />
            )}

            <Input 
              multiline={false} 
              placeholder={getText("value_placeholder")} 
              value={val.value} 
              onChange={(e) => this.changeSearchCond(idx, "value", e.target.value)} 
            />
            <div>
              <FormControlLabel 
                control={<Checkbox checked={val.include} onChange={(e) => this.changeSearchCond(idx, "include", e.target.checked)} />}
                label={<span className={styles.subtext}>{getText("checkbox_include")}</span>}
              />
            </div>
            <div>
              <IconButton onClick={() => this.removeSearchCond(idx)}>
                <RemoveCircle color="error" style={{ fontSize: "28px" }} />
              </IconButton>
            </div>
          </div>
        ))}

        <div className={styles.add_search_cond}>
          <IconButton onClick={() => this.addSearchCond()}>
            <AddCircle color="primary" style={{ fontSize: "28px" }} />
          </IconButton>
        </div>

        <div style={{ textAlign: "center" }}>
          <Button variant="contained" endIcon={<Search />} onClick={() => this.search()}>
            {getText("search")}
          </Button>
        </div>

        <div className={styles.result_content}>
          {this.state.result.map((item) => {
            let label_str_arr = [];

            for (let k in item.label)
              label_str_arr.push(`${k}: ${item.label[k]}`);

            return (
              <Card className={styles['MuiCard-root']}>
                <CardActionArea onClick={() => this.setState({ selected_res: item })}>
                  <CardContent className={styles['MuiCardContent-root']}>
                    {label_str_arr.map((v) => 
                      <Chip 
                        className={styles['LabelChip-root']} 
                        label={v} 
                        color="primary" 
                        avatar={<Avatar className={styles.LabelAvatar}>L</Avatar>} 
                      />
                    )}
                  </CardContent>
                </CardActionArea>
              </Card>
            )
          })}
        </div>

        <div>
          <Drawer 
            anchor="bottom" 
            classes={{
              paper: styles['MuiDrawer-paper'],
              paperAnchorBottom: styles['MuiDrawer-paperAnchorBottom']
            }}
            open={!!this.state.selected_res} 
            onClose={() => this.setState({ selected_res: null })}
          >
            <Box className={styles.detailview_drawerbox}>
              <Grid container>
                <Grid item xs={3} sx={{ "&>:nth-child(n+2)": { mt: 2 } }}>
                  <div>
                    <ToggleButtonGroup value={this.state.detail_view_type_view} exclusive onChange={(e, newval) => this.setDetailViewType(e, "view", newval)}>
                      <ToggleButton value="compare_view"><CompareArrows /></ToggleButton>
                      <ToggleButton value="only_origin_view"><CropOriginal /></ToggleButton>
                      <ToggleButton value="only_cleaned_view"><Verified /></ToggleButton>
                    </ToggleButtonGroup>
                  </div>

                  <div>
                    <ToggleButtonGroup value={this.state.detail_view_type_tool} onChange={(e, newval) => this.setDetailViewType(e, "tool", newval)}>
                      <ToggleButton value="show_check"><Crop /></ToggleButton>
                    </ToggleButtonGroup>
                  </div>
                </Grid>
                <Grid item xs={8} />
                <Grid item xs={1} style={{ textAlign: "right" }}>
                  <IconButton onClick={() => this.setState({ selected_res: null })}>
                    <Close />
                  </IconButton>
                </Grid>
              </Grid>

              <Grid container spacing={4}>
                {this.state.detail_view_type_view === "compare_view" && (
                  <>
                    <Grid item xs={5}>
                      <img 
                        className="detail_view origin_img" 
                        src={`data:image/png;base64,${this.state.detail_view_type_tool.indexOf('show_check') ? this.state.selected_res?.origin_image : this.state.selected_res?.drawed_orgin_image}`} 
                      />
                    </Grid>
                    <Grid item xs={2} />
                    <Grid item xs={5}>
                      <img className="detail_view new_img" src={`data:image/png;base64,${this.state.selected_res?.image}`} />
                    </Grid>
                  </>
                )}
                
                {this.state.detail_view_type_view === "only_origin_view" && (
                  <Grid item xs={6}>
                    <img 
                      className="detail_view origin_img" 
                      src={`data:image/png;base64,${this.state.detail_view_type_tool.indexOf('show_check') ? this.state.selected_res?.origin_image : this.state.selected_res?.drawed_orgin_image}`} 
                    />
                  </Grid>
                )}

                {this.state.detail_view_type_view === "only_cleaned_view" && (
                  <Grid item>
                    <img className="detail_view new_img" src={`data:image/png;base64,${this.state.selected_res?.image}`} loading="eager" />
                  </Grid>
                )}
              </Grid>
            </Box>
          </Drawer>
        </div>
      </>
    )
  }
}

export default ClearedImg